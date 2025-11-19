# core/services/user_service.py
from core.models.user import User
from core.repositories.user_repo import UserRepository
from datetime import datetime, timezone


def utc_now_iso() -> str:
    """Текущее время UTC в формате ISO 8601 с зоной +00:00."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class UserService:
    """Сервис логики пользователей."""

    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_all_users(self):
        """Вернуть список всех пользователей, отсортированных по fio, full_name, username."""
        return await self.repo.get_all_users()

    async def register_if_needed(self, tg_user):
        """
        Автоматическая регистрация (только Telegram поля).
        При первой регистрации created_at выставляется автоматически.
        """
        existing = await self.repo.get(tg_user.id)
        if existing:
            return existing

        now = utc_now_iso()
        user = User(
            user_id=tg_user.id,
            username=tg_user.username,
            full_name=tg_user.full_name,
            created_at=now,
            updated_at=now
        )

        # В repo.upsert автоматически обновится created_at/updated_at при вставке
        await self.repo.upsert(user)
        return user

    async def update_extra_info(
        self,
        user_id: int,
        fio: str | None = None,
        birth_date: str | None = None,
        gender: str | None = None,
        phone: str | None = None,
        email: str | None = None
    ):
        """
        Добровольная дополнительная регистрация.
        Обновляет поля и автоматически обновляет updated_at.
        """
        now = utc_now_iso()
        # Обновляем только переданные поля
        fields_to_update = {
            "fio": fio,
            "birth_date": birth_date,
            "gender": gender,
            "phone": phone,
            "email": email,
            "updated_at": now
        }
        # Удаляем поля, которые None
        fields_to_update = {k: v for k, v in fields_to_update.items() if v is not None}

        if fields_to_update:
            await self.repo.update_extra(user_id=user_id, **fields_to_update)
