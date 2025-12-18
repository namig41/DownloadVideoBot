"""Обработчики обычных сообщений"""
from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message()
async def echo_message(message: Message):
    """Обработчик всех остальных сообщений"""
    await message.answer(
        "Отправьте мне ссылку на короткое видео из:\n"
        "• Instagram\n"
        "• TikTok\n"
        "• YouTube Shorts\n\n"
        "И я скачаю его для вас! Используйте /help для справки."
    )

