import aiogram.types

from Keyboards.Consts.InlineConsts import InlineConstructor


class InlineAdminButtons(InlineConstructor):

    @staticmethod
    def start_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1,1,1]
        btns = [{"text": "Создать пост", "callback_data": "create_post"},
                {"text": "Посмотреть посты", "callback_data": "all_posts"},
                {"text": "Скрыть меню", "callback_data": "hide"}]
        return InlineAdminButtons._create_kb(btns, schema)

    @staticmethod
    def back_kb(skip_mode: bool = False) -> aiogram.types.InlineKeyboardMarkup:

        if skip_mode:
            schema = [1, 1, 1]
            btns = [{"text": "Пропустить", "callback_data": "skip"},
                    {"text": "Назад", "callback_data": "back"},
                    {"text": "Выйти", "callback_data": "menu"}]
        else:
            schema = [1, 1]
            btns = [{"text": "Назад", "callback_data": "back"},
                    {"text": "Выйти", "callback_data": "menu"}]

        return InlineAdminButtons._create_kb(btns, schema)

    @staticmethod
    def approve_reserve(user_id: str) -> aiogram.types.InlineKeyboardMarkup:

        schema = [1, 1]
        btns = [{"text": "Подтвердить", "callback_data": f"approve_{user_id}"},
                {"text": "Отклонить", "callback_data": f"reject_{user_id}"}]

        return InlineAdminButtons._create_kb(btns, schema)

    @staticmethod
    def posts_kb(page: int, last_page: int, buttons: list[dict], previous: bool = False, next: bool = False) -> aiogram.types.InlineKeyboardMarkup:
        schema = []
        btns = []
        for i in buttons:

            schema.append(1)
            btns.append(i)

        if previous == True and next == True:
            schema.append(4)
            btns.append({"text":"<<", "callback_data":f"all_posts-{0}"})
            btns.append({"text": "<", "callback_data": f"all_posts-{page-1}"})
            btns.append({"text": ">", "callback_data": f"all_posts-{page+1}"})
            btns.append({"text": ">>", "callback_data": f"all_posts-{last_page}"})

        elif previous == True and next == False:
            schema.append(2)
            btns.append({"text": "<<", "callback_data": f"all_posts-{0}"})
            btns.append({"text": "<", "callback_data": f"all_posts-{page - 1}"})

        elif previous == False and next == True:
            schema.append(2)
            btns.append({"text": ">", "callback_data": f"all_posts-{page + 1}"})
            btns.append({"text": ">>", "callback_data": f"all_posts-{last_page}"})

        schema.append(1)
        btns.append({"text": "Назад", "callback_data": f"menu"})


        return InlineAdminButtons._create_kb(btns, schema)

    @staticmethod
    def post_kb() -> aiogram.types.InlineKeyboardMarkup:

        schema = [1]
        btns = [{"text": "Назад", "callback_data": "menu"}]

        return InlineAdminButtons._create_kb(btns, schema)

    @staticmethod
    def confirm_post_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1]
        btns = [{"text": "Сейчас", "callback_data": "send_post_now"},
                {"text": "Отменить", "callback_data": "menu"}]
        return InlineAdminButtons._create_kb(btns, schema)

    @staticmethod
    def cancel_post(post_id: str) -> aiogram.types.InlineKeyboardMarkup:
        schema = [1]
        btns = [{"text": "Отменить", "callback_data": f"cancel_{post_id}"}]
        return InlineAdminButtons._create_kb(btns, schema)
