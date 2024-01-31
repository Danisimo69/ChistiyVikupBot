from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    wait_user_data = State()
