"""Обработчики команд бота"""
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from database.database import get_db
from services.user_service import UserService
from config.settings import settings
from bot.keyboards import get_main_keyboard
import asyncio
from datetime import datetime

router = Router()


def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором"""
    admin_ids = [settings.TELEGRAM_ADMINS_ID]
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
            language_code=message.from_user.language_code
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
        "Бесплатно и без ограничений.",
        reply_markup=get_main_keyboard()
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
        "/privacy - Политика конфиденциальности",
        reply_markup=get_main_keyboard()
    )


@router.callback_query(lambda c: c.data == "help")
async def callback_help(callback: CallbackQuery):
    """Обработчик callback кнопки Помощь"""
    await callback.answer()
    # Отправляем новое сообщение, так как callback может быть из другого сообщения
    await callback.message.answer(
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
        "/privacy - Политика конфиденциальности",
        reply_markup=get_main_keyboard()
    )


@router.callback_query(lambda c: c.data == "examples")
async def callback_examples(callback: CallbackQuery):
    """Обработчик callback кнопки Примеры"""
    await callback.answer()
    await callback.message.answer(
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
        "Просто отправьте ссылку на видео из Instagram, TikTok или YouTube Shorts.",
        reply_markup=get_main_keyboard()
    )


@router.callback_query(lambda c: c.data == "stats")
async def callback_stats(callback: CallbackQuery):
    """Обработчик callback кнопки Статистика"""
    await callback.answer()
    # Создаем временный объект Message для передачи в cmd_stats
    # Используем callback.message как основу
    async for session in get_db():
        stats = await UserService.get_user_stats(session, callback.from_user.id)
        if stats:
            # Форматируем имя пользователя
            full_name = ""
            if stats.get('first_name'):
                full_name = stats['first_name']
                if stats.get('last_name'):
                    full_name += f" {stats['last_name']}"
            
            # Форматируем дату регистрации
            created_at = stats.get('created_at')
            created_at_str = "неизвестно"
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    created_at_str = dt.strftime("%d.%m.%Y")
                except:
                    created_at_str = created_at
            
            # Форматируем дату последней активности
            last_activity = stats.get('last_activity')
            last_activity_str = "никогда"
            if last_activity:
                try:
                    dt = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                    last_activity_str = dt.strftime("%d.%m.%Y %H:%M")
                except:
                    last_activity_str = last_activity
            
            # Формируем информацию о пользователе
            user_info = []
            if full_name:
                user_info.append(f"Имя: {full_name}")
            if stats.get('username'):
                user_info.append(f"Username: @{stats['username']}")
            if stats.get('language_code'):
                user_info.append(f"Язык: {stats['language_code'].upper()}")
            
            # Статистика использования
            days_used = stats.get('days_used', 0)
            total_videos = stats.get('total_videos_downloaded', 0)
            total_requests = stats.get('total_requests', 0)
            
            # Вычисляем среднее количество видео в день
            avg_per_day = round(total_videos / days_used, 1) if days_used > 0 else 0
            
            stats_text = (
                f"📊 Ваша статистика:\n\n"
                f"👤 Профиль:\n"
            )
            
            if user_info:
                stats_text += "\n".join(user_info) + "\n"
            else:
                stats_text += "Информация недоступна\n"
            
            stats_text += (
                f"\n📈 Использование:\n"
                f"• Скачано видео: {total_videos}\n"
                f"• Всего запросов: {total_requests}\n"
                f"• Дней использования: {days_used}\n"
                f"• Среднее в день: {avg_per_day} видео\n"
                f"\n🕐 Даты:\n"
                f"• Регистрация: {created_at_str}\n"
                f"• Последняя активность: {last_activity_str}"
            )
            
            await callback.message.answer(
                stats_text,
                reply_markup=get_main_keyboard()
            )
        else:
            await callback.message.answer(
                "Статистика не найдена. Используйте /start для регистрации.",
                reply_markup=get_main_keyboard()
            )
        break


@router.callback_query(lambda c: c.data == "invite")
async def callback_invite(callback: CallbackQuery):
    """Обработчик callback кнопки Пригласить"""
    await callback.answer()
    bot_info = await callback.bot.get_me()
    bot_username = bot_info.username or settings.TELEGRAM_BOT_NAME or "your_bot"
    invite_link = f"https://t.me/{bot_username}?start=ref_{callback.from_user.id}"
    
    invite_text = (
        "👥 Пригласите друзей использовать бота\n\n"
        f"Ссылка для приглашения:\n{invite_link}\n\n"
        "Поделитесь этой ссылкой с друзьями, и они смогут начать использовать бота."
    )
    await callback.message.answer(invite_text, reply_markup=get_main_keyboard())


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
        "Просто отправьте ссылку на видео из Instagram, TikTok или YouTube Shorts.",
        reply_markup=get_main_keyboard()
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
        "По вопросам конфиденциальности обращайтесь к администратору.",
        reply_markup=get_main_keyboard()
    )


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Обработчик команды /stats"""
    async for session in get_db():
        stats = await UserService.get_user_stats(session, message.from_user.id)
        if stats:
            # Форматируем имя пользователя
            full_name = ""
            if stats.get('first_name'):
                full_name = stats['first_name']
                if stats.get('last_name'):
                    full_name += f" {stats['last_name']}"
            
            # Форматируем дату регистрации
            created_at = stats.get('created_at')
            created_at_str = "неизвестно"
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    created_at_str = dt.strftime("%d.%m.%Y")
                except:
                    created_at_str = created_at
            
            # Форматируем дату последней активности
            last_activity = stats.get('last_activity')
            last_activity_str = "никогда"
            if last_activity:
                try:
                    dt = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                    last_activity_str = dt.strftime("%d.%m.%Y %H:%M")
                except:
                    last_activity_str = last_activity
            
            # Формируем информацию о пользователе
            user_info = []
            if full_name:
                user_info.append(f"Имя: {full_name}")
            if stats.get('username'):
                user_info.append(f"Username: @{stats['username']}")
            if stats.get('language_code'):
                user_info.append(f"Язык: {stats['language_code'].upper()}")
            
            # Статистика использования
            days_used = stats.get('days_used', 0)
            total_videos = stats.get('total_videos_downloaded', 0)
            total_requests = stats.get('total_requests', 0)
            
            # Вычисляем среднее количество видео в день
            avg_per_day = round(total_videos / days_used, 1) if days_used > 0 else 0
            
            stats_text = (
                f"📊 Ваша статистика:\n\n"
                f"👤 Профиль:\n"
            )
            
            if user_info:
                stats_text += "\n".join(user_info) + "\n"
            else:
                stats_text += "Информация недоступна\n"
            
            stats_text += (
                f"\n📈 Использование:\n"
                f"• Скачано видео: {total_videos}\n"
                f"• Всего запросов: {total_requests}\n"
                f"• Дней использования: {days_used}\n"
                f"• Среднее в день: {avg_per_day} видео\n"
                f"\n🕐 Даты:\n"
                f"• Регистрация: {created_at_str}\n"
                f"• Последняя активность: {last_activity_str}"
            )
            
            await message.answer(
                stats_text,
                reply_markup=get_main_keyboard()
            )
        else:
            await message.answer(
                "Статистика не найдена. Используйте /start для регистрации.",
                reply_markup=get_main_keyboard()
            )
        break


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Обработчик команды /admin для массовой рассылки"""
    # Проверяем права администратора
    if not is_admin(message.from_user.id):
        await message.answer(
            "У вас нет прав для выполнения этой команды.",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Проверяем, есть ли текст после команды
    command_text = message.text or ""
    parts = command_text.split(maxsplit=1)
    
    if len(parts) < 2:
        await message.answer(
            "Команда массовой рассылки\n\n"
            "Использование: /admin <текст сообщения>\n\n"
            "Пример: /admin Привет. Это массовая рассылка.",
            reply_markup=get_main_keyboard()
        )
        return
    
    broadcast_text = parts[1]
    bot = message.bot
    
    # Получаем всех пользователей
    async for session in get_db():
        users = await UserService.get_all_users(session, limit=10000)
        
        if not users:
            await message.answer(
                "Пользователи не найдены.",
                reply_markup=get_main_keyboard()
            )
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

