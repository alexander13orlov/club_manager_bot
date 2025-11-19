# telegram/routers.py
from aiogram import Dispatcher
from telegram.handlers import users
from telegram.handlers import registration
from telegram.handlers import admin  # ⬅ добавили

def register_routers(dp: Dispatcher, *, user_service=None):
    """
    Центральная точка регистрации всех роутеров проекта
    с поддержкой проброса зависимостей.
    """

    # -------------------- users router --------------------
    if user_service is not None:
        dp.include_router(users.get_router(user_service))
    else:
        try:
            dp.include_router(users.router)
        except Exception:
            pass

    # -------------------- registration (FSM) --------------------
    try:
        dp.include_router(registration.router)
    except Exception:
        pass

    # -------------------- admin router --------------------
    # admin принимает user_service → пробрасываем вручную
    try:
        admin.register_admin_handlers(dp, user_service)
    except Exception:
        pass
