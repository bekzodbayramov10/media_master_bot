import asyncio
import glob
import os
import tempfile
import uuid

import yt_dlp
from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from common import (
    MAX_SIZE,
    URL_CACHE,
    URL_RE,
    download_audio_url,
    identify_and_show,
)

router = Router()


def download_video(url: str, outdir: str):
    opts = {
        "outtmpl": f"{outdir}/%(id)s.%(ext)s",
        "format": "bv*[height<=720]+ba/b[height<=720]/b",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_color": True,
        "max_filesize": MAX_SIZE,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    files = glob.glob(f"{outdir}/*")
    return files[0] if files else None


# --- havola -> video (pastida musiqa tugmalari bilan) ---
@router.message(F.text.regexp(URL_RE))
async def handle_link(message: Message):
    url = URL_RE.search(message.text).group(0)
    status = await message.answer("⏳ Video yuklanmoqda...")
    try:
        with tempfile.TemporaryDirectory() as tmp:
            path = await asyncio.to_thread(download_video, url, tmp)
            if not path or os.path.getsize(path) > MAX_SIZE:
                await status.edit_text("Video topilmadi yoki 50 MB dan katta.")
                return

            token = uuid.uuid4().hex[:10]
            URL_CACHE[token] = url
            kb = InlineKeyboardBuilder()
            kb.button(text="📥 Qo'shiqni yuklab olish", callback_data=f"vaudio:{token}")
            kb.button(text="🔊 Videodagi ovozni olish", callback_data=f"vraw:{token}")
            kb.adjust(1)

            await message.answer_video(
                FSInputFile(path),
                caption="@media_master_bot orqali yuklab olindi 🚀",
                reply_markup=kb.as_markup(),
            )
        await status.delete()
    except Exception as e:
        await status.edit_text(f"Xatolik: {str(e)[:300]}")


# --- tugma: videodagi musiqani aniqlash ---
@router.callback_query(F.data.startswith("vaudio:"))
async def cb_video_find(call: CallbackQuery):
    url = URL_CACHE.get(call.data.split(":", 1)[1])
    if not url:
        await call.answer("Tugma eskirgan, havolani qayta yuboring.", show_alert=True)
        return
    await call.answer("Musiqa aniqlanmoqda...")
    status = await call.message.answer("🎧 Videodagi musiqa aniqlanmoqda...")
    try:
        with tempfile.TemporaryDirectory() as tmp:
            path, _ = await asyncio.to_thread(download_audio_url, url, tmp)
            if not path:
                await status.edit_text("Videodan ovoz olib bo'lmadi.")
                return
            await identify_and_show(status, path)
    except ImportError:
        await status.edit_text(
            "Shazam kutubxonasi o'rnatilmagan.\n"
            "Terminalda: py -3.12 -m pip install shazamio"
        )
    except Exception as e:
        await status.edit_text(f"Xatolik: {str(e)[:300]}")


# --- tugma: videodagi ovozning o'zini olish ---
@router.callback_query(F.data.startswith("vraw:"))
async def cb_video_raw(call: CallbackQuery):
    url = URL_CACHE.get(call.data.split(":", 1)[1])
    if not url:
        await call.answer("Tugma eskirgan, havolani qayta yuboring.", show_alert=True)
        return
    await call.answer("Ovoz yuklanmoqda...")
    status = await call.message.answer("⏳ Ovoz yuklanmoqda...")
    try:
        with tempfile.TemporaryDirectory() as tmp:
            path, title = await asyncio.to_thread(download_audio_url, url, tmp)
            if not path or os.path.getsize(path) > MAX_SIZE:
                await status.edit_text("Ovoz topilmadi yoki 50 MB dan katta.")
                return
            await call.message.answer_audio(FSInputFile(path), title=title)
        await status.delete()
    except Exception as e:
        await status.edit_text(f"Xatolik: {str(e)[:300]}")