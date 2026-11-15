import os
from pydantic_settings import BaseSettings
from pydantic import Field


class BotSettings(BaseSettings):
    BOT_TOKEN: str = Field(default="")
    BACKEND_URL: str = Field(default="http://backend:8000")
    ADMIN_API_KEY: str = Field(default="tinvix_secret_admin_key_2026")

    # URL to open in Telegram Mini App (e.g. https://xxxx.trycloudflare.com or https://your-domain.com)
    MINI_APP_URL: str = Field(default="http://localhost")

    # Specific Administrator Telegram user IDs (comma-separated, e.g. "12345678,98765432")
    # Empty string means NO admins are configured. Random users cannot add products!
    ADMIN_IDS: str = Field(default="")

    BOT_MODE: str = Field(default="polling")  # "polling" or "webhook"
    WEBHOOK_HOST: str = Field(default="")
    WEBHOOK_PATH: str = Field(default="/bot-webhook")
    WEBHOOK_PORT: int = Field(default=8080)
    WEBHOOK_SECRET: str = Field(default="my-webhook-secret-token")

    def is_admin(self, user_id: int) -> bool:
        if not self.ADMIN_IDS or not self.ADMIN_IDS.strip():
            return False
        # Parse comma-separated IDs
        admins = [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip().isdigit()]
        return user_id in admins

    class Config:
        env_file = ".env"
        extra = "allow"


settings = BotSettings()
