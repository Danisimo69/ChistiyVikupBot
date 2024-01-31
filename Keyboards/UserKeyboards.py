import aiogram.types

from Keyboards.Consts.InlineConsts import InlineConstructor


class InlineButtons(InlineConstructor):
    @staticmethod
    def start_kb__not_sub(text, url) -> aiogram.types.InlineKeyboardMarkup:
        schema = [1]
        btns = [{"text": text, "url": url}]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def default_post_kb(id) -> aiogram.types.InlineKeyboardMarkup:
        schema = [2,2]
        btns = [{"text": "Подробнее", "url": f"https://t.me/Chistiy_vikup_bot?start=info_{id}"},
                {"text": "Бронь", "url": f"https://t.me/Chistiy_vikup_bot?start=reserve_{id}"},
                {"text": "Менеджер", "url": f"https://t.me/chistiy_vikup"},
                {"text": "Больше фото", "url": f"https://t.me/Chistiy_vikup_bot?start=photo_{id}"}]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def payment_kb(id) -> aiogram.types.InlineKeyboardMarkup:
        schema = [1]
        btns = [{"text": "Далее", "callback_data": f"payment_{id}"}]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def reject_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1]
        btns = [{"text": "Менеджер", "url": f"https://t.me/chistiy_vikup"}]
        return InlineButtons._create_kb(btns, schema)
