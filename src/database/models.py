from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, Text, Date, UniqueConstraint
from sqlalchemy.orm import declarative_base
from datetime import datetime, date

Base = declarative_base()


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, nullable=False, unique=True, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), nullable=True)
    
    # Статистика
    total_requests = Column(Integer, default=0)
    total_videos_downloaded = Column(Integer, default=0)
    
    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, nullable=True)
    
    # Дополнительные данные (JSON в виде текста)
    extra_data = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"

