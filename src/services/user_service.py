from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from datetime import datetime, date
from typing import Optional, Tuple
from database.models import User


class UserService:
    """Сервис для работы с пользователями"""
    
    @staticmethod
    async def get_or_create_user(
        session: AsyncSession,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: Optional[str] = None,
        is_premium: bool = False,
        is_bot: bool = False
    ) -> User:
        """Получить пользователя или создать нового"""
        # Ищем существующего пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Обновляем данные пользователя
            user.username = username or user.username
            user.first_name = first_name or user.first_name
            user.last_name = last_name or user.last_name
            user.language_code = language_code or user.language_code
            user.is_premium = is_premium
            user.is_bot = is_bot
            user.last_activity = datetime.utcnow()
            user.updated_at = datetime.utcnow()
        else:
            # Создаем нового пользователя
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                language_code=language_code,
                is_premium=is_premium,
                is_bot=is_bot,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                daily_attempts=0,
                last_attempt_date=date.today()
            )
            session.add(user)
        
        await session.commit()
        await session.refresh(user)
        return user
    
    @staticmethod
    async def get_user(session: AsyncSession, telegram_id: int) -> Optional[User]:
        """Получить пользователя по telegram_id"""
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def increment_requests(session: AsyncSession, telegram_id: int):
        """Увеличить счетчик запросов"""
        await session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(
                total_requests=User.total_requests + 1,
                last_activity=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )
        await session.commit()
    
    @staticmethod
    async def increment_photos_processed(session: AsyncSession, telegram_id: int):
        """Увеличить счетчик обработанных фото"""
        await session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(
                total_photos_processed=User.total_photos_processed + 1,
                last_activity=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )
        await session.commit()
    
    @staticmethod
    async def increment_videos_downloaded(session: AsyncSession, telegram_id: int):
        """Увеличить счетчик скачанных видео"""
        await session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(
                total_videos_downloaded=User.total_videos_downloaded + 1,
                last_activity=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )
        await session.commit()
    
    @staticmethod
    async def get_user_stats(session: AsyncSession, telegram_id: int) -> Optional[dict]:
        """Получить статистику пользователя"""
        user = await UserService.get_user(session, telegram_id)
        if not user:
            return None
        
        return {
            "telegram_id": user.telegram_id,
            "username": user.username,
            "total_requests": user.total_requests,
            "total_photos_processed": user.total_photos_processed,
            "total_videos_downloaded": user.total_videos_downloaded,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_activity": user.last_activity.isoformat() if user.last_activity else None,
        }
    
    @staticmethod
    async def get_all_users(session: AsyncSession, limit: int = 100, offset: int = 0) -> list[User]:
        """Получить список всех пользователей"""
        query = select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
        
        result = await session.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_total_users_count(session: AsyncSession) -> int:
        """Получить общее количество пользователей"""
        query = select(func.count(User.id))
        result = await session.execute(query)
        return result.scalar() or 0
