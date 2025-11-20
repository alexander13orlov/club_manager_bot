# admin_schedule_states.py
from aiogram.fsm.state import StatesGroup, State

class MoveSessionStates(StatesGroup):
    waiting_for_new_time = State()
    waiting_for_trainer = State()

class AddExtraSessionStates(StatesGroup):
    waiting_for_details = State()
