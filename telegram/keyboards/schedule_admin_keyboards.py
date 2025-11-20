# telegram/keyboards/schedule_admin_keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_session_keyboard(inst_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Отменить", callback_data=f"cancel:{inst_id}"),
                InlineKeyboardButton(text="Перенести", callback_data=f"move:{inst_id}"),
                InlineKeyboardButton(text="Сменить тренера", callback_data=f"change_trainer:{inst_id}")
            ]
        ]
    )

def extra_session_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Добавить доп. занятие", callback_data="add_extra")]
        ]
    )
