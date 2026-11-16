from pydantic_settings import BaseSettings
from pydantic import Field


class BotSettings(BaseSettings):
    BOT_TOKEN: str = Field(default="9119830014:AAHk8_DEMO_TOKEN_FOR_TINVIX_BOT_2026")
    BACKEND_URL: str = Field(default="http://backend:8000")
    ADMIN_API_KEY: str = Field(default="tinvix_secret_admin_key_2026")
    MINI_APP_URL: str = Field(default="https://tinvix.onrender.com")
    ADMIN_IDS: str = Field(default="9119830014,123456789")
    BOT_MODE: str = Field(default="webhook")
    WEBHOOK_HOST: str = Field(default="https://tinvix.onrender.com")
    WEBHOOK_PATH: str = Field(default="/bot-webhook")
    WEBHOOK_PORT: int = Field(default=8080)
    WEBHOOK_SECRET: str = Field(default="my-webhook-secret-token")

    def is_admin(self, user_id: int) -> bool:
        if not self.ADMIN_IDS or not self.ADMIN_IDS.strip():
            return False
        admins = [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip().isdigit()]
        return user_id in admins

    class Config:
        env_file = ".env"
        extra = "allow"


settings = BotSettings()
