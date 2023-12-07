from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres@localhost:5432/weenat"
    DATA_APP_BASE_URL: str = "http://localhost:3000"


settings = Settings()
