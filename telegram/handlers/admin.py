# telegram/handlers/admin.py
from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command

from config import ADMINS
from core.services.user_service import UserService
import csv
from pathlib import Path

def register_admin_handlers(dp, user_service: UserService):

    router = Router()

    @router.message(Command("users"))
    async def cmd_users(message: Message):
        # Проверяем, что это админ
        if message.from_user.id not in ADMINS:
            return await message.answer("❌ Команда доступна только администраторам.")

        users = await user_service.get_all_users()
        if not users:
            return await message.answer("Пока нет зарегистрированных пользователей.")

        # ---------- Сортировка ----------
        users_sorted = sorted(
            users,
            key=lambda u: (
                u.fio.lower() if u.fio else "",
                u.full_name.lower() if u.full_name else "",
                u.username.lower() if u.username else ""
            )
        )

                # ---------- 1) Вывод в текст ----------
        text_lines = ["📋 <b>Список пользователей:</b>\n"]
        for idx, u in enumerate(users_sorted, start=1):
            text_lines.append(
                f"{idx}. {u.user_id} — {u.full_name or 'Без имени'} - {u.fio or ''}"
            )


        await message.answer("\n".join(text_lines))

        # ---------- 2) Выдача CSV ----------
        csv_path = Path("users_export.csv")

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([
                "user_id", "full_name", "username", "fio",
                "birth_date", "gender", "phone", "email",
                "created_at", "updated_at"
            ])
            for u in users_sorted:
                writer.writerow([
                    u.user_id, u.full_name, u.username, u.fio,
                    u.birth_date, u.gender, u.phone, u.email,
                    u.created_at, u.updated_at
                ])

        await message.answer_document(FSInputFile(csv_path))

    dp.include_router(router)
