import io
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from bot.config import settings
from bot.services.api_client import api_client

logger = logging.getLogger(__name__)
router = Router(name="admin")


def get_admin_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="🛍️ Открыть каталог",
                web_app=WebAppInfo(url=settings.MINI_APP_URL),
            )
        ],
        [
            InlineKeyboardButton(
                text="➕ Создать товар",
                callback_data="prompt_create_product",
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data == "prompt_create_product")
async def cb_prompt_create_product(callback: CallbackQuery):
    if not settings.is_admin(callback.from_user.id):
        await callback.answer(
            f"🚫 У вас нет прав администратора. Ваш ID: {callback.from_user.id}",
            show_alert=True,
        )
        return

    await callback.answer()
    await callback.message.answer(
        "📸 **Создание товара**\n\n"
        "Отправьте **название и фото в одном сообщении** (прикрепите фото и в поле «Подпись / Caption» напишите название товара).",
        parse_mode="Markdown",
    )


@router.message(F.text.casefold().in_(["создать товар", "/create", "/new_product", "добавить товар"]))
async def cmd_create_product_instruction(message: Message):
    if not settings.is_admin(message.from_user.id):
        await message.answer(
            f"🚫 У вас нет прав администратора для создания товаров.\n"
            f"Ваш Telegram ID: `{message.from_user.id}`.\n"
            f"Для предоставления прав добавьте этот ID в параметр `ADMIN_IDS` в файле `.env`.",
            parse_mode="Markdown",
        )
        return

    await message.answer(
        "📸 **Создание товара**\n\n"
        "Отправьте **название и фото в одном сообщении**:\n"
        "Прикрепите фото и укажите название товара в подписи (caption).",
        parse_mode="Markdown",
        reply_markup=get_admin_keyboard(),
    )


@router.message(F.photo & F.caption)
async def handle_photo_with_caption(message: Message, bot: Bot):
    if not settings.is_admin(message.from_user.id):
        await message.answer(
            f"🚫 У вас нет прав администратора для добавления товаров.\n"
            f"Ваш Telegram ID: `{message.from_user.id}`.",
            parse_mode="Markdown",
        )
        return

    title = message.caption.strip()
    if not title:
        await message.answer("⚠️ Название товара не может быть пустым. Отправьте фото с названием в подписи.")
        return

    status_msg = await message.answer("⏳ Сохраняю фото в MinIO S3 и создаю товар в PostgreSQL...")

    try:
        # Get highest resolution photo
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)

        # Download strictly in-memory (stateless, no local disk storage)
        buffer = io.BytesIO()
        await bot.download_file(file_info.file_path, destination=buffer)
        file_bytes = buffer.getvalue()

        filename = f"tg_{photo.file_unique_id}.jpg"

        # Upload via backend service (which handles MinIO + PostgreSQL + idempotency)
        product = await api_client.create_product(
            title=title,
            file_bytes=file_bytes,
            filename=filename,
            content_type="image/jpeg",
            telegram_file_id=photo.file_unique_id,
        )

        catalog_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🛍️ Посмотреть в каталоге",
                        web_app=WebAppInfo(url=settings.MINI_APP_URL),
                    )
                ]
            ]
        )

        await status_msg.edit_text(
            f"✅ **Товар успешно создан!**\n\n"
            f"🆔 ID: `{product.get('id')}`\n"
            f"📦 Название: **{product.get('title')}**\n"
            f"🖼️ Изображение сохранено в MinIO S3\n"
            f"💾 Запись внесена в PostgreSQL",
            parse_mode="Markdown",
            reply_markup=catalog_kb,
        )
    except Exception as e:
        logger.exception("Failed to create product from bot: %s", e)
        await status_msg.edit_text(f"❌ Ошибка при создании товара: {str(e)}")


@router.message(F.photo & ~F.caption)
async def handle_photo_without_caption(message: Message):
    if settings.is_admin(message.from_user.id):
        await message.answer(
            "⚠️ Вы отправили фотографию без подписи!\n\n"
            "По ТЗ название и фото должны быть отправлены **в одном сообщении**.\n"
            "Пожалуйста, отправьте фото с названием в поле «Добавить подпись» (caption).",
        )
