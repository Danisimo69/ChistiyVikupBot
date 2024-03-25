from aiogram.fsm.state import StatesGroup, State


class AdminStates(StatesGroup):
    create_post_name = State()
    create_post_photos = State()
    create_post_info = State()
    create_post_more_photos = State()
    create_post_more_photos_plus = State()
    create_post_confirm = State()
