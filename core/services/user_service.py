from core.models.user import User
from core.repositories.user_repo import UserRepository


class UserService:
    """Сервис логики пользователей."""

    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def register_if_needed(self, tg_user):
        """Автоматическая регистрация (только Telegram поля)."""
        existing = await self.repo.get(tg_user.id)
        if existing:
            return existing

        user = User(
            user_id=tg_user.id,
            username=tg_user.username,
            full_name=tg_user.full_name
        )

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
        """Добровольная дополнительная регистрация."""
        await self.repo.update_extra(
            user_id=user_id,
            fio=fio,
            birth_date=birth_date,
            gender=gender,
            phone=phone,
            email=email
        )
