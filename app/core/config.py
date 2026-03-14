from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Threat Intelligence API"
    database_url: str = "sqlite:///challenge/threat_intel.db"


settings = Settings()
