from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_URL: str = "sqlite:///./database.db"
    SECRET_KEY: str  # wajib dari .env; aplikasi sengaja gagal start bila kosong
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    DATASET_PATH: str = "data/survey_results_public_2025.xlsx"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
