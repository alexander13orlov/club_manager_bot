# telegram/handlers/admin_schedule.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import date, timedelta
import logging

from aiogram.exceptions import TelegramAPIError  # Aiogram 3

from core.services.schedule_service import ScheduleService
from core.services.user_service import UserService
from telegram.keyboards.schedule_admin_keyboards import (
    admin_session_keyboard,
    extra_session_keyboard,
)
from .admin_schedule_states import MoveSessionStates, AddExtraSessionStates

router = Router()
logger = logging.getLogger(__name__)

def get_admin_schedule_router(
    schedule_service: ScheduleService,
    user_service: UserService
) -> Router:

    RU_WEEKDAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

    async def format_trainer_name(user_id: int) -> str:
        user = await user_service.repo.get(user_id)
        if not user:
            return f"#{user_id}"
        if user.fio:
            return user.fio
        elif user.username:
            return user.username
        elif user.full_name:
            return user.full_name
        else:
            return f"#{user_id}"

    # ----------------- Расписание на сегодня -----------------
    @router.message(Command("schedule_today"))
    async def schedule_today(message: Message):
        today = date.today()
        instances = schedule_service.build_daily_schedule(today)

        if not instances:
            await message.answer("Сегодня занятий нет.")
            return

        weekday_name = RU_WEEKDAYS[today.weekday()]

        for inst in instances:
            trainer_name = await format_trainer_name(inst.trainer_id)
            await message.answer(
                f"{inst.id}) {inst.training_type} {inst.start_time.strftime('%H:%M')} "
                f"({inst.duration_minutes} мин), тренер: {trainer_name}, зал: {inst.place}, статус: {inst.status}",
                reply_markup=admin_session_keyboard(inst.id)
            )

        await message.answer("Управление занятиями:", reply_markup=extra_session_keyboard())

    # ----------------- Расписание на неделю -----------------
    @router.message(Command("schedule_week"))
    async def schedule_week(message: Message):
        today = date.today()
        for i in range(7):
            day = today + timedelta(days=i)
            weekday_name = RU_WEEKDAYS[day.weekday()]
            instances = schedule_service.build_daily_schedule(day)
            text = f"📅 {day.isoformat()} ({weekday_name})"
            if not instances:
                await message.answer(f"{text}\n  Занятий нет")
            else:
                for inst in instances:
                    trainer_name = await format_trainer_name(inst.trainer_id)
                    await message.answer(
                        f"{inst.id}) {inst.training_type} {inst.start_time.strftime('%H:%M')} "
                        f"({inst.duration_minutes} мин), тренер: {trainer_name}, зал: {inst.place}, статус: {inst.status}",
                        reply_markup=admin_session_keyboard(inst.id)
                    )
        await message.answer("Управление занятиями:", reply_markup=extra_session_keyboard())

    # ----------------- Обработка inline callback -----------------
    @router.callback_query(F.data)
    async def admin_schedule_callback(query: CallbackQuery, state: FSMContext):
        data = query.data
        user_id = query.from_user.id

        try:
            if data.startswith("cancel:"):
                inst_id = int(data.split(":")[1])
                schedule_service.cancel(inst_id=inst_id, admin_id=user_id, reason="Через телеграм")
                await query.answer("Занятие отменено ✅")
                try:
                    await query.message.edit_reply_markup(reply_markup=admin_session_keyboard(inst_id))
                except TelegramAPIError as e:
                    if "message is not modified" in str(e):
                        pass
                    else:
                        raise

            elif data.startswith("move:"):
                inst_id = int(data.split(":")[1])
                await state.update_data(inst_id=inst_id)
                await query.message.answer("Введите новое время занятия (HH:MM):")
                await state.set_state(MoveSessionStates.waiting_for_new_time)

            elif data.startswith("change_trainer:"):
                inst_id = int(data.split(":")[1])
                await state.update_data(inst_id=inst_id)
                await query.message.answer("Введите ID нового тренера:")
                await state.set_state(MoveSessionStates.waiting_for_trainer)

            elif data == "add_extra":
                await query.message.answer("Введите дату нового занятия (YYYY-MM-DD):")
                await state.set_state(AddExtraSessionStates.waiting_for_details)

            else:
                await query.answer("Неизвестная команда ❌")

        except Exception as e:
            await query.answer(f"Ошибка: {e}", show_alert=True)
            logger.exception("Ошибка при обработке коллбека админа")

    return router
