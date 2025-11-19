# core/services/user_service.py
from core.models.user import User
from core.repositories.user_repo import UserRepository


class UserService:
    """Сервис логики пользователей."""

    def __init__(self, repo: UserRepository):
        self.repo = repo
    
    async def get_all_users(self):
        """Вернуть список всех пользователей."""
        return await self.repo.get_all_users()

    # ------------------- REGISTRATION -------------------

    async def register_if_needed(self, tg_user):
        """
        Автоматическая регистрация.
        Only inserts if user does not exist.
        """

        existing = await self.repo.get(tg_user.id)

        if existing:
            # Пользователь был зарегистрирован, просто синхронизируем
            return await self.refresh_telegram_fields(existing, tg_user)

        # Создаём нового пользователя — timestamps создаст SQLite
        user = User(
            user_id=tg_user.id,
            username=tg_user.username,
            full_name=tg_user.full_name,
        )

        await self.repo.upsert(user)
        return user

    async def refresh_telegram_fields(self, existing: User, tg_user):
        """
        Обновляет username / full_name, если они изменились в Telegram.
        Это вызывает обновление updated_at в БД.
        """

        changed = False

        username = tg_user.username or None
        full_name = tg_user.full_name or None

        if existing.username != username:
            existing.username = username
            changed = True

        if existing.full_name != full_name:
            existing.full_name = full_name
            changed = True

        if changed:
            await self.repo.upsert(existing)

        return existing

    # ------------------- EXTRA FIELDS -------------------

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
        Обновляет дополнительные пользовательские поля.
        updated_at ставится автоматически в repo.update_extra().
        """

        await self.repo.update_extra(
            user_id=user_id,
            fio=fio,
            birth_date=birth_date,
            gender=gender,
            phone=phone,
            email=email
        )

