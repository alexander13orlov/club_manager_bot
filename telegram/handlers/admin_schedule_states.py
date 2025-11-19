# telegram/handlers/admin_schedule_states.py
from aiogram.fsm.state import StatesGroup, State

class MoveSessionStates(StatesGroup):
    waiting_for_new_time = State()  # ждем ввода нового времени

class AddExtraSessionStates(StatesGroup):
    waiting_for_details = State()   # ждем ввода данных нового занятия
