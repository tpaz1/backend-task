from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "dev"
    log_level: str = "INFO"
    log_json: bool = False

    openai_api_key: str = ""
    openai_base_url: str = "https://api.aim.security/fw/v1/proxy/openai"


settings = Settings()
