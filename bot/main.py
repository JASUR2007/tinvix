import asyncio
import logging
import os
import socket
import sys
import time
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import MenuButtonWebApp, WebAppInfo
from fastapi import FastAPI, Request, Response

from bot.config import settings
from bot.handlers import admin_router, start_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("tinvix-bot")

INSTANCE_ID = f"{socket.gethostname()}-{os.getpid()}"


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    # admin router first so photo/caption handlers catch product creation
    dp.include_router(admin_router)
    dp.include_router(start_router)
    return dp


async def setup_menu_button(bot: Bot):
    if not settings.MINI_APP_URL:
        return
    try:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="Каталог",
                web_app=WebAppInfo(url=settings.MINI_APP_URL),
            )
        )
        logger.info("Chat menu button configured with Mini App URL: %s", settings.MINI_APP_URL)
    except Exception as e:
        logger.warning("Could not set chat menu button: %s", e)


async def run_polling(bot: Bot, dp: Dispatcher):
    logger.info("Starting bot [%s] in POLLING mode...", INSTANCE_ID)
    await bot.delete_webhook(drop_pending_updates=True)
    await setup_menu_button(bot)
    await dp.start_polling(bot)


def run_webhook(bot: Bot, dp: Dispatcher):
    logger.info("Starting bot [%s] in WEBHOOK mode on port %s...", INSTANCE_ID, settings.WEBHOOK_PORT)
    app = FastAPI(title="Tinvix Bot Webhook Receiver")

    @app.on_event("startup")
    async def on_startup():
        await setup_menu_button(bot)
        if settings.WEBHOOK_HOST:
            webhook_url = f"{settings.WEBHOOK_HOST.rstrip('/')}{settings.WEBHOOK_PATH}"
            logger.info("Registering Telegram Webhook to: %s", webhook_url)
            try:
                await bot.set_webhook(
                    url=webhook_url,
                    secret_token=settings.WEBHOOK_SECRET,
                    drop_pending_updates=True,
                )
                logger.info("Webhook registered successfully.")
            except Exception as e:
                logger.error("Failed to register webhook: %s", e)

    @app.post(settings.WEBHOOK_PATH)
    async def telegram_update(request: Request):
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if settings.WEBHOOK_SECRET and secret != settings.WEBHOOK_SECRET:
            logger.warning("Received update with invalid secret token!")
            return Response(status_code=403, content="Invalid secret token")

        data = await request.json()
        await dp.feed_raw_update(bot, data)
        return Response(status_code=200, content="OK")

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "service": "tinvix-bot-webhook",
            "instance_id": INSTANCE_ID,
        }

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.WEBHOOK_PORT)


def main():
    if not settings.BOT_TOKEN or "YOUR_" in settings.BOT_TOKEN or ":" not in settings.BOT_TOKEN:
        logger.warning("=" * 60)
        logger.warning("⚠️  BOT_TOKEN не настроен в .env!")
        logger.warning("Укажите реальный токен от @BotFather в файле .env")
        logger.warning("Контейнер бота запущен в режиме ожидания.")
        logger.warning("=" * 60)
        while True:
            time.sleep(3600)

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = build_dispatcher()

    if settings.BOT_MODE.lower() == "webhook":
        run_webhook(bot, dp)
    else:
        asyncio.run(run_polling(bot, dp))


if __name__ == "__main__":
    main()
