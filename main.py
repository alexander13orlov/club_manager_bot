# main.py
import asyncio
import logging
from telegram.bot import bot, dp
from telegram.handlers.registration import register_registration_handlers
from telegram.routers import register_routers
from core.repositories.user_repo import UserRepository
from core.services.user_service import UserService
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

# -------------------- Main --------------------
async def main():
    # создаём асинхронный репозиторий
    user_repo = await UserRepository.create(str(USERS_FILE))
    user_service = UserService(user_repo)

    # middleware: автоматическая регистрация пользователей
    dp.message.middleware(UserRegistrationMiddleware(user_service))

    # регистрируем FSM-обработчики регистрации
    register_registration_handlers(dp, user_service)

    # регистрируем остальные роутеры, включая admin
    register_routers(dp, user_service=user_service)

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

# -------------------- Entry point --------------------
if __name__ == "__main__":
    asyncio.run(main())
