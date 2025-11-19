# telegram/handlers/admin_schedule.py

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from datetime import date, timedelta
from core.services.schedule_service import ScheduleService
from core.services.user_service import UserService

def get_admin_schedule_router(
    schedule_service: ScheduleService,
    user_service: UserService
) -> Router:
    router = Router()

    RU_WEEKDAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

    async def format_trainer_name(user_id: int) -> str:
        """Возвращает отображаемое имя тренера по приоритету fio → username → full_name"""
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

    @router.message(Command("schedule_today"))
    async def schedule_today(message: Message):
        today = date.today()
        instances = schedule_service.build_daily_schedule(today)

        if not instances:
            await message.answer("Сегодня занятий нет.")
            return

        weekday_name = RU_WEEKDAYS[today.weekday()]
        lines = [f"📅 {today.isoformat()} ({weekday_name})"]

        for inst in instances:
            trainer_name = await format_trainer_name(inst.trainer_id)
            lines.append(
                f"{inst.id}) {inst.training_type} {inst.start_time.strftime('%H:%M')} "
                f"({inst.duration_minutes} мин), тренер: {trainer_name}, зал: {inst.place}, статус: {inst.status}"
            )

        await message.answer("\n".join(lines))

    @router.message(Command("schedule_week"))
    async def schedule_week(message: Message):
        today = date.today()
        lines = []

        for i in range(7):
            day = today + timedelta(days=i)
            weekday_name = RU_WEEKDAYS[day.weekday()]
            instances = schedule_service.build_daily_schedule(day)
            lines.append(f"📅 {day.isoformat()} ({weekday_name}):")
            if not instances:
                lines.append("  Занятий нет")
            else:
                for inst in instances:
                    trainer_name = await format_trainer_name(inst.trainer_id)
                    lines.append(
                        f"  {inst.id}) {inst.training_type} {inst.start_time.strftime('%H:%M')} "
                        f"({inst.duration_minutes} мин), тренер: {trainer_name}, зал: {inst.place}, статус: {inst.status}"
                    )
            lines.append("")  # пустая строка между днями

        await message.answer("\n".join(lines))

    return router
