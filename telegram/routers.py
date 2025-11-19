# telegram/routers.py
from aiogram import Dispatcher
from telegram.handlers import users
from telegram.handlers import registration
from telegram.handlers import admin  # legacy admin handlers

from telegram.handlers.admin_schedule import get_admin_schedule_router

def register_routers(dp: Dispatcher, *, user_service=None, schedule_service=None):
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

    # -------------------- legacy admin router --------------------
    try:
        admin.register_admin_handlers(dp, user_service)
    except Exception:
        pass

    # -------------------- admin_schedule router --------------------
    if schedule_service is not None and user_service is not None:
        dp.include_router(get_admin_schedule_router(schedule_service=schedule_service, user_service=user_service))
