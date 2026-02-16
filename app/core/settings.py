from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_URL: str = "sqlite:///./database.db"
    SECRET_KEY: str = "not-very-secret"

    JWT_EXPIRE_MINUTES: int = 1

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
