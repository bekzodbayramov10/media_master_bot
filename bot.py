import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

import image_handlers
import music_handlers
import video_handlers
from common import BOT_TOKEN, ENV_PATH
from texts import LANGS, get_lang, set_lang, t, variants

logging.basicConfig(level=logging.INFO)
dp = Dispatcher()


def main_menu(uid):
    kb = ReplyKeyboardBuilder()
    for key in ("btn_video", "btn_music", "btn_voice", "btn_image", "btn_lang"):
        kb.button(text=t(uid, key))
    kb.adjust(2)
    return kb.as_markup(
        resize_keyboard=True,
        input_field_placeholder=t(uid, "placeholder"),
    )


def lang_keyboard():
    kb = InlineKeyboardBuilder()
    for code, name in LANGS.items():
        kb.button(text=name, callback_data=f"lang:{code}")
    kb.adjust(1)
    return kb.as_markup()


async def ask_language(message: Message):
    await message.answer(
        t(message.chat.id, "choose_lang"), reply_markup=lang_keyboard()
    )


@dp.message(CommandStart())
async def cmd_start(message: Message):
    uid = message.chat.id
    if get_lang(uid) is None:
        await ask_language(message)
        return
    await message.answer(t(uid, "welcome"), reply_markup=main_menu(uid))


@dp.message(Command("language"))
async def cmd_language(message: Message):
    await ask_language(message)


@dp.message(Command("menu"))
async def cmd_menu(message: Message):
    uid = message.chat.id
    await message.answer(t(uid, "menu_title"), reply_markup=main_menu(uid))


@dp.message(Command("help"))
async def cmd_help(message: Message):
    uid = message.chat.id
    await message.answer(t(uid, "help"), reply_markup=main_menu(uid))


@dp.callback_query(F.data.startswith("lang:"))
async def cb_lang(call: CallbackQuery):
    code = call.data.split(":", 1)[1]
    if code not in LANGS:
        await call.answer()
        return
    uid = call.message.chat.id
    set_lang(uid, code)
    await call.message.edit_text(t(uid, "lang_set"))
    await call.message.answer(t(uid, "welcome"), reply_markup=main_menu(uid))
    await call.answer()


# --- menyu tugmalari (barcha tillarda taniladi) ---
@dp.message(F.text.in_(variants("btn_lang")))
async def btn_lang(message: Message):
    await ask_language(message)


@dp.message(F.text.in_(variants("btn_video")))
async def btn_video(message: Message):
    await message.answer(t(message.chat.id, "hint_video"))


@dp.message(F.text.in_(variants("btn_music")))
async def btn_music(message: Message):
    await message.answer(t(message.chat.id, "hint_music"))


@dp.message(F.text.in_(variants("btn_voice")))
async def btn_voice(message: Message):
    await message.answer(t(message.chat.id, "hint_voice"))


@dp.message(F.text.in_(variants("btn_image")))
async def btn_image(message: Message):
    await message.answer(t(message.chat.id, "hint_image"))


# Tartib muhim: havola (video) matn qidiruvidan oldin tekshiriladi
dp.include_router(video_handlers.router)
dp.include_router(music_handlers.router)
dp.include_router(image_handlers.router)


async def main():
    if not BOT_TOKEN:
        print("BOT_TOKEN topilmadi:", ENV_PATH)
        return
    print("Token topildi, bot ishga tushyapti...")
    bot = Bot(token=BOT_TOKEN, session=AiohttpSession(timeout=300))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
