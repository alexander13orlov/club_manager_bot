# telegram/routers.py
from aiogram import Dispatcher
from telegram.handlers import users
from telegram.handlers import registration  # если есть

def register_routers(dp: Dispatcher, *, user_service=None):
    if user_service is not None:
        dp.include_router(users.get_router(user_service))
    else:
        try:
            dp.include_router(users.router)
        except Exception:
            pass

    # подключаем router регистрации (FSM)
    try:
        dp.include_router(registration.router)
    except Exception:
        # registration может требовать зависимости — если так, импортируй и передай
        pass
