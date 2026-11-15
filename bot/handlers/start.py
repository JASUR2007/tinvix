from aiogram import Router, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from bot.config import settings

router = Router(name="start")


def get_catalog_inline_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="🛍️ Открыть каталог",
                web_app=WebAppInfo(url=settings.MINI_APP_URL),
            )
        ]
    ]
    if is_admin:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="➕ Создать товар",
                    callback_data="prompt_create_product",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_reply_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(
                text="🛍️ Каталог",
                web_app=WebAppInfo(url=settings.MINI_APP_URL),
            )
        ]
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text="➕ Создать товар")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
    )


@router.message(F.text.startswith("/start"))
async def cmd_start(message: Message):
    is_admin = settings.is_admin(message.from_user.id)
    text = "У меня есть товар"

    await message.answer(
        text,
        reply_markup=get_reply_keyboard(is_admin),
    )
    await message.answer(
        "Нажмите кнопку ниже, чтобы открыть каталог товаров:",
        reply_markup=get_catalog_inline_keyboard(is_admin),
    )


@router.message(~F.photo)
async def fallback_any_message(message: Message):
    is_admin = settings.is_admin(message.from_user.id)
    # По ТЗ при обычном обращении бот сообщает: «У меня есть товар» и предлагает открыть Mini App с каталогом.
    await message.answer(
        "У меня есть товар",
        reply_markup=get_catalog_inline_keyboard(is_admin),
    )
