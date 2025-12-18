from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    PYTHONPATH: str
    
    # Bot token
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_BOT_NAME: str
    TELEGRAM_ADMINS_ID: int
    
    # PostgreSQL
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

