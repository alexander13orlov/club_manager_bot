import asyncio
import logging
import sqlite3
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from telegram.bot import bot  # твой бот
from telegram.handlers.registration import register_registration_handlers
from telegram.routers import register_routers
from core.repositories.user_repo import UserRepository
from core.repositories.schedule_repo import (
    BaseScheduleTemplateRepo,
    TrainingInstanceRepo,
    ScheduleChangeLogRepo
)
from core.services.user_service import UserService
from core.services.schedule_service import ScheduleService
from telegram.middlewares.user_registration import UserRegistrationMiddleware
from config import USERS_FILE, LOGS_DIR

# -------------------- Logging --------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
file_handler = logging.FileHandler(LOGS_DIR / "bot.log", encoding="utf8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"))
logging.getLogger().addHandler(file_handler)
logging.getLogger("aiogram").setLevel(logging.DEBUG)
logging.getLogger("aiohttp").setLevel(logging.WARNING)

# -------------------- FSM Storage --------------------
storage = MemoryStorage()
dp: Dispatcher = Dispatcher(storage=storage)

# -------------------- Main --------------------
async def main():
    # создаём асинхронный репозиторий пользователей
    user_repo = await UserRepository.create(str(USERS_FILE))
    user_service = UserService(user_repo)

    # создаём sqlite-соединение для расписания
    conn = sqlite3.connect("data/club_schedule.db", check_same_thread=False)
    base_repo = BaseScheduleTemplateRepo(conn)
    inst_repo = TrainingInstanceRepo(conn)
    log_repo = ScheduleChangeLogRepo(conn)

    # создаём сервис расписания
    schedule_service = ScheduleService(
        base_repo=base_repo,
        inst_repo=inst_repo,
        log_repo=log_repo
    )

    # middleware: автоматическая регистрация пользователей
    dp.message.middleware(UserRegistrationMiddleware(user_service))

    # регистрируем FSM-обработчики регистрации
    register_registration_handlers(dp, user_service)

    # регистрируем остальные роутеры, включая админские
    register_routers(dp, user_service=user_service, schedule_service=schedule_service)

    # запуск polling
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logging.info("Bot stopped by KeyboardInterrupt")
    finally:
        # закрываем ресурсы
        try:
            await user_repo.close()
        except Exception as e:
            logging.exception("Error closing user_repo: %s", e)
        try:
            await bot.session.close()
        except Exception:
            pass
        conn.close()

# -------------------- Entry point --------------------
if __name__ == "__main__":
    asyncio.run(main())
