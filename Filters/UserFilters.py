from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


class Redact_Card_Filter(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        try:
            return True if callback.data.split("_")[1] in ["old", "new"] else False
        except:
            return False
