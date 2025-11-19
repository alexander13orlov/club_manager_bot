# telegram/handlers/users.py
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from core.services.user_service import UserService

# router factory — возвращает Router, привязанный к указанному UserService
def get_router(user_service: UserService) -> Router:
    router = Router()

    @router.message(Command("start"))
    async def cmd_start(message: Message):
        # Обязательно await, метод - асинхронный
        await user_service.register_if_needed(message.from_user)
        text = (
            "<b>Добро пожаловать!</b>\n"
            "Вы зарегистрированы в системе.\n"
            "Используйте /profile, чтобы посмотреть данные.\n"
        )
        await message.answer(text, parse_mode="HTML")

    @router.message(Command("profile"))
    async def cmd_profile(message: Message):
        # get - асинхронный, надо await
        u = await user_service.repo.get(message.from_user.id)
        if not u:
            return await message.reply("Профиль не найден. Отправьте /register")

        username_display = f"@{u.username}" if u.username else "—"

        await message.reply(
            "<b>Ваш профиль:</b>\n"
            f"Telegram ID: {u.user_id}\n"
            f"Username: {username_display}\n"
            f"ФИО: {u.fio or '—'}\n"
            f"Дата рождения: {u.birth_date or '—'}\n"
            f"Пол: {u.gender or '—'}\n"
            f"Телефон: {u.phone or '—'}\n"
            f"Email: {u.email or '—'}\n",
            parse_mode="HTML",
        )

    return router
