"""Обработчики команд бота"""
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from database.database import get_db
from services.user_service import UserService
from config.settings import settings
import asyncio
from datetime import datetime

router = Router()


def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором"""
    admin_ids = settings.get_admin_ids()
    return user_id in admin_ids


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
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
    
    # Формируем приветствие
    user_name = message.from_user.first_name or message.from_user.username
    greeting = f"Привет, {user_name}" if user_name else "Привет"
    
    await message.answer(
        f"{greeting}\n\n"
        "🎥 Видео загрузчик\n\n"
        "Я помогу вам скачать видео из:\n"
        "• Instagram\n"
        "• TikTok\n"
        "• YouTube Shorts\n\n"
        "Просто отправьте мне ссылку на видео, и я скачаю его для вас.\n"
        "Поддерживаются видео до 5 минут.\n\n"
        "Бесплатно и без ограничений."
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await message.answer(
        "Как использовать:\n\n"
        "1. Отправьте ссылку на видео из:\n"
        "   • Instagram\n"
        "   • TikTok\n"
        "   • YouTube Shorts\n"
        "2. Получите скачанное видео\n\n"
        "Просто скопируйте и отправьте ссылку - бот автоматически распознает её и начнет скачивание.\n\n"
        "Поддерживаются видео до 5 минут. Более длинные видео не скачиваются.\n\n"
        "Команды:\n"
        "/stats - Посмотреть вашу статистику\n"
        "/examples - Примеры использования\n"
        "/privacy - Политика конфиденциальности"
    )


@router.message(Command("examples"))
async def cmd_examples(message: Message):
    """Обработчик команды /examples"""
    await message.answer(
        "Примеры использования:\n\n"
        "1. Сохранение понравившегося видео из TikTok\n"
        "   Отправьте ссылку на видео, чтобы сохранить его для просмотра позже\n\n"
        "2. Создание личной коллекции контента\n"
        "   Собирайте интересные видео из разных платформ в одном месте\n\n"
        "3. Офлайн просмотр видео\n"
        "   Скачайте видео для просмотра без интернета\n\n"
        "4. Сохранение видео для дальнейшего использования\n"
        "   Используйте скачанные видео для создания собственного контента\n\n"
        "Как использовать:\n"
        "Просто отправьте ссылку на видео из Instagram, TikTok или YouTube Shorts."
    )


@router.message(Command("privacy"))
async def cmd_privacy(message: Message):
    """Обработчик команды /privacy"""
    await message.answer(
        "Политика конфиденциальности:\n\n"
        "Бот собирает и хранит только необходимую информацию для работы:\n"
        "• Telegram ID пользователя\n"
        "• Статистика использования (количество запросов, скачанных видео)\n"
        "• Дата последней активности\n\n"
        "Данные используются исключительно для:\n"
        "• Предоставления услуг бота\n"
        "• Улучшения работы сервиса\n"
        "• Статистики использования\n\n"
        "Гарантии:\n"
        "• Видео удаляются сразу после отправки пользователю\n"
        "• Данные не передаются третьим лицам\n"
        "• Данные не используются для рекламы\n\n"
        "По вопросам конфиденциальности обращайтесь к администратору."
    )


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Обработчик команды /stats"""
    async for session in get_db():
        stats = await UserService.get_user_stats(session, message.from_user.id)
        if stats:
            # Форматируем дату последней активности
            last_activity = stats.get('last_activity')
            if last_activity:
                try:
                    # Парсим ISO формат и форматируем в читаемый вид
                    dt = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                    last_activity_str = dt.strftime("%d.%m.%Y %H:%M")
                except:
                    last_activity_str = last_activity
            else:
                last_activity_str = "никогда"
            
            await message.answer(
                f"📊 Ваша статистика:\n\n"
                f"Пользователь: @{stats['username'] or 'без имени'}\n"
                f"Скачано видео: {stats['total_videos_downloaded']}\n"
                f"Всего запросов: {stats['total_requests']}\n"
                f"Последняя активность: {last_activity_str}"
            )
        else:
            await message.answer("Статистика не найдена. Используйте /start для регистрации.")
        break


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Обработчик команды /admin для массовой рассылки"""
    # Проверяем права администратора
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    
    # Проверяем, есть ли текст после команды
    command_text = message.text or ""
    parts = command_text.split(maxsplit=1)
    
    if len(parts) < 2:
        await message.answer(
            "Команда массовой рассылки\n\n"
            "Использование: /admin <текст сообщения>\n\n"
            "Пример: /admin Привет. Это массовая рассылка."
        )
        return
    
    broadcast_text = parts[1]
    bot = message.bot
    
    # Получаем всех пользователей
    async for session in get_db():
        users = await UserService.get_all_users(session, limit=10000)
        
        if not users:
            await message.answer("Пользователи не найдены.")
            return
        
        total_users = len(users)
        successful = 0
        failed = 0
        
        # Отправляем сообщение о начале рассылки
        status_msg = await message.answer(
            f"Начинаю рассылку сообщения {total_users} пользователям\n\n"
            f"Сообщение: {broadcast_text[:100]}..."
        )
        
        # Рассылаем сообщения
        for user in users:
            try:
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=broadcast_text
                )
                successful += 1
                # Небольшая задержка, чтобы не превысить лимиты Telegram
                await asyncio.sleep(0.05)
            except Exception as e:
                failed += 1
                # Логируем ошибки, но продолжаем рассылку
                continue
        
        # Обновляем статус
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            text=(
                f"Рассылка завершена\n\n"
                f"Статистика:\n"
                f"• Всего пользователей: {total_users}\n"
                f"• Успешно отправлено: {successful}\n"
                f"• Ошибок: {failed}"
            )
        )
        break

