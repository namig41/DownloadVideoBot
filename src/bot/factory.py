"""Создание и настройка диспетчера бота"""
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from database.database import init_db
from bot.handlers.commands import router as commands_router
from bot.handlers.video import router as video_router
from bot.handlers.messages import router as messages_router
from config.settings import settings


def create_dispatcher() -> Dispatcher:
    """Создает и настраивает диспетчер бота"""
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрируем роутеры
    dp.include_router(commands_router)
    dp.include_router(video_router)
    dp.include_router(messages_router)
    
    # Регистрируем обработчики событий
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    return dp


async def on_startup():
    """Инициализация при запуске бота"""
    await init_db()


async def on_shutdown():
    """Очистка при остановке бота"""
    pass


async def main():
    """Главная функция запуска бота"""
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = create_dispatcher()
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
