"""Обработчики обычных сообщений"""
from aiogram import Router
from aiogram.types import Message
from bot.keyboards import get_main_keyboard

router = Router()


@router.message()
async def echo_message(message: Message):
    """Обработчик всех остальных сообщений"""
    await message.answer(
        "Отправьте мне ссылку на видео из:\n"
        "• Instagram\n"
        "• TikTok\n"
        "• YouTube Shorts\n\n"
        "И я скачаю его для вас. Используйте /help для справки.",
        reply_markup=get_main_keyboard()
    )

