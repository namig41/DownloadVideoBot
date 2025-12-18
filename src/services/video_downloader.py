"""Сервис для скачивания видео"""
import yt_dlp
import os
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


async def download_video(url: str, bot_id: str = "video_downloader", max_duration: int = 300) -> Dict:
    """
    Скачивает короткие видео из Instagram, TikTok, YouTube Shorts
    
    Args:
        url: URL видео
        bot_id: ID бота для создания директории
        max_duration: Максимальная длительность видео в секундах (по умолчанию 300 = 5 минут)
        
    Returns:
        dict с путем к файлу и метаданными или ошибкой
    """
    logger.info(f"Начинаю скачивание видео: {url}")
    try:
        # Создаем директорию для загрузок
        downloads_dir = Path("downloads") / bot_id
        downloads_dir.mkdir(parents=True, exist_ok=True)
        
        # Настройки yt-dlp
        ydl_opts = {
            'format': 'best',
            'outtmpl': str(downloads_dir / '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        
        # Сначала получаем информацию о видео без скачивания
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Получаем информацию о видео без скачивания
            info = ydl.extract_info(url, download=False)
            duration = info.get("duration", 0)
            
            # Проверяем длительность видео
            if duration > max_duration:
                logger.warning(f"Видео слишком длинное: {duration} секунд (максимум {max_duration})")
                return {
                    "status": "failed",
                    "error": f"Видео слишком длинное ({duration} секунд). Поддерживаются только короткие видео до {max_duration} секунд."
                }
            
            # Если это YouTube, проверяем, что это Shorts
            if "youtube.com" in url or "youtu.be" in url:
                # Проверяем, что это Shorts или короткое видео
                if "shorts" not in url.lower() and duration > max_duration:
                    return {
                        "status": "failed",
                        "error": f"Поддерживаются только YouTube Shorts или короткие видео до {max_duration} секунд."
                    }
            
            # Скачиваем видео
            logger.info(f"Скачиваю видео длительностью {duration} секунд")
            ydl_opts_download = ydl_opts.copy()
            ydl_opts_download['quiet'] = False  # Включаем вывод для отслеживания прогресса
            with yt_dlp.YoutubeDL(ydl_opts_download) as ydl_download:
                info = ydl_download.extract_info(url, download=True)
                filename = ydl_download.prepare_filename(info)
                
                # Если файл был переименован, находим его
                if not os.path.exists(filename):
                    # Ищем файл в директории
                    files = list(downloads_dir.glob("*"))
                    if files:
                        # Берем самый новый файл
                        files.sort(key=os.path.getmtime, reverse=True)
                        filename = str(files[0])
            
            result = {
                "status": "completed",
                "file_path": filename,
                "title": info.get("title", "video"),
                "caption": info.get("title", "Видео"),
                "duration": duration,
            }
            
            logger.info(f"Видео успешно скачано: {filename}")
            return result
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e).lower()
        logger.error(f"Ошибка при скачивании видео {url}: {e}", exc_info=True)
        
        # Обрабатываем различные типы ошибок
        if "private" in error_msg or "unavailable" in error_msg:
            return {
                "status": "failed",
                "error": (
                    "Видео недоступно для скачивания.\n\n"
                    "Возможные причины:\n"
                    "• Видео является приватным\n"
                    "• Видео было удалено\n"
                    "• Доступ к видео ограничен\n\n"
                    "Проверьте ссылку и убедитесь, что видео публичное."
                )
            }
        elif "unable to download" in error_msg or "network" in error_msg:
            return {
                "status": "failed",
                "error": (
                    "Не удалось подключиться к серверу.\n\n"
                    "Попробуйте:\n"
                    "• Проверить интернет-соединение\n"
                    "• Повторить попытку через несколько секунд\n"
                    "• Убедиться, что ссылка корректна"
                )
            }
        elif "sign in" in error_msg or "login" in error_msg:
            return {
                "status": "failed",
                "error": (
                    "Для доступа к этому видео требуется авторизация.\n\n"
                    "К сожалению, бот не может скачивать приватные или защищенные видео."
                )
            }
        elif "age-restricted" in error_msg or "age" in error_msg:
            return {
                "status": "failed",
                "error": (
                    "Видео имеет возрастные ограничения.\n\n"
                    "Бот не может скачивать контент с возрастными ограничениями."
                )
            }
        else:
            return {
                "status": "failed",
                "error": (
                    "Не удалось скачать видео.\n\n"
                    "Возможные причины:\n"
                    "• Неверная ссылка\n"
                    "• Видео недоступно\n"
                    "• Проблемы с сервером платформы\n\n"
                    "Проверьте ссылку и попробуйте снова."
                )
            }
    except Exception as e:
        logger.error(f"Неожиданная ошибка при скачивании видео {url}: {e}", exc_info=True)
        return {
            "status": "failed",
            "error": (
                "Произошла ошибка при обработке запроса.\n\n"
                "Попробуйте:\n"
                "• Проверить правильность ссылки\n"
                "• Повторить попытку позже\n"
                "• Использовать /help для получения справки"
            )
        }

