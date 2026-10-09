import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import image_handlers
import music_handlers
import video_handlers
from common import BOT_TOKEN, ENV_PATH

BTN_VIDEO = "🎬 Video yuklash"
BTN_MUSIC = "🎵 Musiqa qidirish"
BTN_VOICE = "🎤 Ovozdan musiqa topish"
BTN_IMAGE = "🖼 Rasm orqa fonini o'chirish"

logging.basicConfig(level=logging.INFO)
dp = Dispatcher()


def main_menu():
    kb = ReplyKeyboardBuilder()
    for text in (BTN_VIDEO, BTN_MUSIC, BTN_VOICE, BTN_IMAGE):
        kb.button(text=text)
    kb.adjust(2)
    return kb.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Havola, qo'shiq nomi yoki rasm yuboring",
    )


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Assalomu alaykum! MediaMaster botiga xush kelibsiz.\n\n"
        "Pastdagi tugmalardan birini tanlang 👇",
        reply_markup=main_menu(),
    )


@dp.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer("Menyu 👇", reply_markup=main_menu())


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "🎬 Video: havolani yuboring (YouTube, TikTok, Instagram...)\n"
        "🎵 Musiqa: qo'shiq nomi yoki ijrochisini yozing\n"
        "🎤 Ovozdan topish: ovozli xabar, audio yoki video yuboring\n"
        "🖼 Rasm: rasmni yuboring, orqa fonini olib tashlayman\n\n"
        "Menyuni qaytarish: /menu",
        reply_markup=main_menu(),
    )


# --- menyu tugmalari: faqat nima qilish kerakligini tushuntiradi ---
@dp.message(F.text == BTN_VIDEO)
async def btn_video(message: Message):
    await message.answer(
        "🎬 Video havolasini yuboring (YouTube, TikTok, Instagram...).\n"
        "Video kelgach, ostidagi tugma orqali undagi qo'shiqni topishingiz mumkin."
    )


@dp.message(F.text == BTN_MUSIC)
async def btn_music(message: Message):
    await message.answer(
        "🎵 Qo'shiq nomi yoki ijrochisini yozing.\n"
        "Masalan: Rauf Faik"
    )


@dp.message(F.text == BTN_VOICE)
async def btn_voice(message: Message):
    await message.answer(
        "🎤 Ovozli xabar, audio yoki video yuboring.\n"
        "Musiqani aniqlab, to'liq variantlarini topib beraman."
    )


@dp.message(F.text == BTN_IMAGE)
async def btn_image(message: Message):
    await message.answer(
        "🖼 Rasmni yuboring, orqa fonini olib tashlayman.\n"
        "Natija shaffof fonli PNG fayl bo'lib keladi."
    )


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