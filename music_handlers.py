import asyncio
import os
import tempfile
from pathlib import Path

from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile, Message

from common import (
    MAX_SIZE,
    SEARCH_CACHE,
    download_audio_url,
    identify_and_show,
    render_page,
    search_music,
)

router = Router()
TG_DOWNLOAD_LIMIT = 20 * 1024 * 1024  # botlar 20 MB gacha fayl yuklab ola oladi


# --- ovozli xabar / audio / video -> musiqani aniqlash ---
@router.message(F.voice | F.audio | F.video | F.video_note)
async def handle_media(message: Message):
    media = message.voice or message.audio or message.video or message.video_note
    if (media.file_size or 0) > TG_DOWNLOAD_LIMIT:
        await message.answer("Fayl 20 MB dan katta. Qisqaroq qismini yuboring.")
        return

    if message.voice:
        ext = ".ogg"
    elif message.audio:
        ext = Path(message.audio.file_name or "").suffix or ".mp3"
    else:
        ext = ".mp4"

    status = await message.answer("🎧 Musiqa aniqlanmoqda...")
    try:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / f"input{ext}"
            await message.bot.download(media, destination=dest)
            await identify_and_show(status, str(dest))
    except ImportError:
        await status.edit_text(
            "Shazam kutubxonasi o'rnatilmagan.\n"
            "Terminalda: py -3.12 -m pip install shazamio"
        )
    except Exception as e:
        await status.edit_text(f"Xatolik: {str(e)[:300]}")


# --- oddiy matn -> musiqa qidirish (ro'yxat) ---
@router.message(F.text, ~F.text.startswith("/"))
async def handle_music(message: Message):
    query = message.text.strip()
    status = await message.answer(f"🔎 Qidirilmoqda: {query}")
    try:
        results = await asyncio.to_thread(search_music, query)
        if not results:
            await status.edit_text("Hech narsa topilmadi.")
            return
        SEARCH_CACHE[(status.chat.id, status.message_id)] = {
            "query": query,
            "results": results,
        }
        text, kb = render_page(query, results, 0)
        await status.edit_text(text, reply_markup=kb)
    except Exception as e:
        await status.edit_text(f"Xatolik: {str(e)[:300]}")


# --- ro'yxat tugmalari ---
@router.callback_query(F.data.startswith("page:"))
async def cb_page(call: CallbackQuery):
    key = (call.message.chat.id, call.message.message_id)
    data = SEARCH_CACHE.get(key)
    if not data:
        await call.answer("Qidiruv eskirgan, qayta yozing.", show_alert=True)
        return
    page = int(call.data.split(":")[1])
    text, kb = render_page(data["query"], data["results"], page)
    await call.message.edit_text(text, reply_markup=kb)
    await call.answer()


@router.callback_query(F.data == "close")
async def cb_close(call: CallbackQuery):
    SEARCH_CACHE.pop((call.message.chat.id, call.message.message_id), None)
    await call.message.delete()
    await call.answer()


@router.callback_query(F.data.startswith("pick:"))
async def cb_pick(call: CallbackQuery):
    key = (call.message.chat.id, call.message.message_id)
    data = SEARCH_CACHE.get(key)
    if not data:
        await call.answer("Qidiruv eskirgan, qayta yozing.", show_alert=True)
        return
    idx = int(call.data.split(":")[1])
    item = data["results"][idx]
    await call.answer("Yuklanmoqda...")
    status = await call.message.answer(f"⏳ Yuklanmoqda: {item['title']}")
    try:
        with tempfile.TemporaryDirectory() as tmp:
            url = f"https://www.youtube.com/watch?v={item['id']}"
            path, _ = await asyncio.to_thread(download_audio_url, url, tmp)
            if not path or os.path.getsize(path) > MAX_SIZE:
                await status.edit_text("Musiqa topilmadi yoki 50 MB dan katta.")
                return
            await call.message.answer_audio(FSInputFile(path), title=item["title"])
        await status.delete()
    except Exception as e:
        await status.edit_text(f"Xatolik: {str(e)[:300]}")