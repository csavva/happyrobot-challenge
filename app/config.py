from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str | None = None
    api_key: str = "dev-change-me"
    environment: str = "development"
    fmcsa_web_key: str | None = None


settings = Settings()
