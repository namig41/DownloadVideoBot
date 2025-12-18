from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Bot token
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_BOT_NAME: str = ""
    TELEGRAM_ADMINS_ID: str = ""
    
    # PostgreSQL
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "video_downloader"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    def get_admin_ids(self) -> list[int]:
        """Получить список ID администраторов"""
        if not self.TELEGRAM_ADMINS_ID:
            return []
        return [int(admin_id.strip()) for admin_id in self.TELEGRAM_ADMINS_ID.split(",") if admin_id.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

