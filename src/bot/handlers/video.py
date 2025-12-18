"""Обработчики для скачивания видео"""
from aiogram import Router
from aiogram.types import Message, FSInputFile
from database import get_db
from services.user_service import UserService
from services.video_downloader import download_video
import re
import os

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
    status_msg = await message.answer("⏳ Начинаю скачивание видео...")
    
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
                    await status_msg.edit_text("✅ Видео готово! Отправляю...")
                    video_file = FSInputFile(file_path)
                    await message.bot.send_video(
                        chat_id=message.chat.id,
                        video=video_file
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
                    await status_msg.edit_text(
                        f"✅ Видео готово, но произошла ошибка при отправке: {str(e)}"
                    )
            else:
                await status_msg.edit_text(
                    f"✅ Задача выполнена: {result.get('message', 'Готово')}"
                )
        else:
            # Ошибка при скачивании
            error = result.get("error", "Неизвестная ошибка")
            await status_msg.edit_text(f"❌ Ошибка: {error}")
    except Exception as e:
        await status_msg.edit_text(f"❌ Произошла ошибка: {str(e)}")
