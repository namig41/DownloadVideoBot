"""Клавиатуры для бота"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Главная клавиатура с основными командами"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📖 Помощь", callback_data="help"),
                InlineKeyboardButton(text="💡 Примеры", callback_data="examples")
            ],
            [
                InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
                InlineKeyboardButton(text="👥 Пригласить", callback_data="invite")
            ]
        ]
    )
    return keyboard

