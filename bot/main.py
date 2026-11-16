import asyncio
import logging
import os
import socket
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import MenuButtonWebApp, WebAppInfo
from fastapi import FastAPI, Request, Response
import uvicorn

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
        logger.info("Menu button configured: %s", settings.MINI_APP_URL)
    except Exception as e:
        logger.warning("Could not set menu button: %s", e)


async def run_polling(bot: Bot, dp: Dispatcher):
    logger.info("Starting bot [%s] in POLLING mode...", INSTANCE_ID)
    try:
        await bot.delete_webhook(drop_pending_updates=False)
        await setup_menu_button(bot)
    except Exception as e:
        logger.warning("Polling setup warning: %s", e)

    port = int(os.getenv("PORT", settings.WEBHOOK_PORT))
    health_app = FastAPI()

    @health_app.get("/")
    @health_app.get("/health")
    @health_app.get("/bot-webhook")
    @health_app.get("/bot-webhook/health")
    async def health():
        return {"status": "ok", "mode": "polling", "instance_id": INSTANCE_ID}

    cfg = uvicorn.Config(health_app, host="0.0.0.0", port=port, log_level="warning")
    server = uvicorn.Server(cfg)

    await asyncio.gather(dp.start_polling(bot), server.serve())


def run_webhook(bot: Bot, dp: Dispatcher):
    port = int(os.getenv("PORT", settings.WEBHOOK_PORT))
    logger.info("Starting bot [%s] in WEBHOOK on port %s...", INSTANCE_ID, port)
    app = FastAPI(title="Tinvix Bot Webhook")

    @app.on_event("startup")
    async def on_startup():
        try:
            await setup_menu_button(bot)
            if settings.WEBHOOK_HOST and "onrender.com" in settings.WEBHOOK_HOST:
                url = f"{settings.WEBHOOK_HOST.rstrip('/')}{settings.WEBHOOK_PATH}"
                await bot.set_webhook(url=url, secret_token=settings.WEBHOOK_SECRET, drop_pending_updates=False)
                logger.info("Webhook set: %s", url)
        except Exception as e:
            logger.warning("Webhook registration note: %s", e)

    @app.post(settings.WEBHOOK_PATH)
    async def telegram_update(request: Request):
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if settings.WEBHOOK_SECRET and secret != settings.WEBHOOK_SECRET:
            return Response(status_code=403, content="Invalid secret")
        data = await request.json()
        await dp.feed_raw_update(bot, data)
        return Response(status_code=200, content="OK")

    @app.get("/")
    @app.get("/health")
    @app.get("/bot-webhook")
    @app.get("/bot-webhook/health")
    async def health():
        return {"status": "ok", "mode": "webhook", "instance_id": INSTANCE_ID}

    uvicorn.run(app, host="0.0.0.0", port=port)


def main():
    if not settings.BOT_TOKEN or "YOUR_" in settings.BOT_TOKEN or ":" not in settings.BOT_TOKEN:
        logger.warning("BOT_TOKEN is not configured.")
        return

    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = build_dispatcher()

    if settings.BOT_MODE.lower() == "webhook":
        run_webhook(bot, dp)
    else:
        asyncio.run(run_polling(bot, dp))


if __name__ == "__main__":
    main()
