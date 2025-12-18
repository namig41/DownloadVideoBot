from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from pathlib import Path
import os
from src.config import settings

# Формируем URL базы данных
# Если указаны настройки PostgreSQL, используем PostgreSQL, иначе SQLite
# Проверяем, что все необходимые поля заполнены

# Создаем движок
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

# Создаем фабрику сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncSession:
    """Получить сессию базы данных"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Инициализация базы данных (создание таблиц)"""
    from .models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Закрыть соединение с базой данных"""
    await engine.dispose()

