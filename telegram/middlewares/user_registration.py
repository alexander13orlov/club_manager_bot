# telegram/middlewares/user_registration.py
from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any

from core.services.user_service import UserService

class UserRegistrationMiddleware(BaseMiddleware):
    def __init__(self, user_service: UserService):
        super().__init__()
        self.user_service = user_service

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        tg_user = getattr(event, "from_user", None)
        if tg_user:
            # Асинхронная регистрация
            await self.user_service.register_if_needed(tg_user)
        return await handler(event, data)