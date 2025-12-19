"""Обработчики для скачивания видео"""
from aiogram import Router
from aiogram.types import Message, FSInputFile
from database import get_db
from services.user_service import UserService
from services.video_downloader import download_video
from bot.keyboards import get_main_keyboard
import re
import os
import logging

logger = logging.getLogger(__name__)

router = Router()


def is_video_url(text: str) -> bool:
    """Проверяет, является ли текст ссылкой на видео"""
    patterns = [
        r'https?://(www\.)?instagram\.com/.+',
        r'https?://(www\.)?(vm\.)?tiktok\.com/.+',
        r'https?://(www\.)?(m\.)?youtube\.com/shorts/.+',
        r'https?://youtu\.be/.+'
    ]
    return any(re.match(pattern, text.strip()) for pattern in patterns)


@router.message(lambda m: m.text and is_video_url(m.text))
async def process_video_url(message: Message):
    """Обработка ссылок на видео (Instagram, TikTok, YouTube Shorts)"""
    url = message.text.strip()
    
    # Регистрируем пользователя
    async for session in get_db():
        await UserService.get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language_code=message.from_user.language_code,
            is_premium=getattr(message.from_user, 'is_premium', False),
            is_bot=message.from_user.is_bot
        )
        
        await UserService.increment_requests(session, message.from_user.id)
    
    # Отправляем сообщение о начале обработки
    status_msg = await message.answer("⏳ Начинаю скачивание видео")
    
    try:
        # Скачиваем видео напрямую
        result = await download_video(url)
        
        # Обрабатываем результат
        if result.get("status") == "completed":
            file_path = result.get("file_path")
            
            # Увеличиваем счетчик скачанных видео
            async for session in get_db():
                await UserService.increment_videos_downloaded(session, message.from_user.id)
            
            if file_path and os.path.exists(file_path):
                try:
                    await status_msg.edit_text("✅ Видео готово. Отправляю")
                    video_file = FSInputFile(file_path)
                    # Отправляем видео без клавиатуры
                    await message.bot.send_video(
                        chat_id=message.chat.id,
                        video=video_file
                    )
                    
                    # Отправляем меню отдельным сообщением
                    await message.bot.send_message(
                        chat_id=message.chat.id,
                        text="Выберите действие:",
                        reply_markup=get_main_keyboard()
                    )
                    
                    # Удаляем временное сообщение о статусе
                    try:
                        await status_msg.delete()
                    except:
                        pass
                    
                    # Удаляем скачанный файл после отправки
                    try:
                        os.remove(file_path)
                    except:
                        pass
                except Exception as e:
                    error_msg = str(e).lower()
                    if "file too large" in error_msg or "file_size" in error_msg:
                        await status_msg.edit_text(
                            "Видео готово, но файл слишком большой для отправки в Telegram.\n\n"
                            "Максимальный размер файла в Telegram: 50 МБ.\n"
                            "Попробуйте скачать видео с меньшим разрешением или сократить длительность.",
                            reply_markup=get_main_keyboard()
                        )
                    elif "timeout" in error_msg or "timed out" in error_msg:
                        await status_msg.edit_text(
                            "Видео готово, но произошла ошибка при отправке из-за таймаута.\n\n"
                            "Попробуйте запросить видео снова.",
                            reply_markup=get_main_keyboard()
                        )
                    else:
                        await status_msg.edit_text(
                            "Видео готово, но произошла ошибка при отправке.\n\n"
                            "Попробуйте запросить видео снова или обратитесь в поддержку.",
                            reply_markup=get_main_keyboard()
                        )
            else:
                await status_msg.edit_text(
                    f"Задача выполнена: {result.get('message', 'Готово')}",
                    reply_markup=get_main_keyboard()
                )
        else:
            # Ошибка при скачивании
            error = result.get("error", "Неизвестная ошибка")
            await status_msg.edit_text(
                f"❌ {error}",
                reply_markup=get_main_keyboard()
            )
    except Exception as e:
        logger.error(f"Критическая ошибка при обработке видео: {e}", exc_info=True)
        await status_msg.edit_text(
            "❌ Произошла критическая ошибка при обработке запроса.\n\n"
            "Попробуйте:\n"
            "• Проверить правильность ссылки\n"
            "• Повторить попытку через несколько секунд\n"
            "• Использовать /help для получения справки",
            reply_markup=get_main_keyboard()
        )
