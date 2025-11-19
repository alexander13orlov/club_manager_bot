from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def admin_session_keyboard(instance_id: int) -> InlineKeyboardMarkup:
    """
    Inline-кнопки для управления конкретным занятием:
    - ❌ Отменить
    - 🔀 Перенести
    - 👤 Сменить тренера
    """
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("❌ Отменить", callback_data=f"cancel:{instance_id}"),
        InlineKeyboardButton("🔀 Перенести", callback_data=f"move:{instance_id}")
    )
    kb.add(
        InlineKeyboardButton("👤 Сменить тренера", callback_data=f"change_trainer:{instance_id}")
    )
    return kb


def extra_session_keyboard() -> InlineKeyboardMarkup:
    """
    Inline-кнопка для добавления одноразового занятия.
    Используется, чтобы админ мог вызвать FSM для ввода данных нового занятия.
    """
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("➕ Добавить занятие", callback_data="add_extra")
    )
    return kb


def admin_day_schedule_keyboard(instances: list[int]) -> InlineKeyboardMarkup:
    """
    Дополнительно: кнопки для быстрого управления всем днём.
    Например, массовая отмена всех занятий или добавление extra.
    """
    kb = InlineKeyboardMarkup(row_width=2)
    for inst_id in instances:
        kb.add(
            InlineKeyboardButton(f"❌ {inst_id}", callback_data=f"cancel:{inst_id}"),
            InlineKeyboardButton(f"🔀 {inst_id}", callback_data=f"move:{inst_id}")
        )
    kb.add(
        InlineKeyboardButton("➕ Добавить занятие", callback_data="add_extra")
    )
    return kb
