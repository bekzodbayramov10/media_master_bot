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
from texts import t

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
    uid = message.chat.id
    url = URL_RE.search(message.text).group(0)
    status = await message.answer(t(uid, "video_loading"))
    try:
        with tempfile.TemporaryDirectory() as tmp:
            path = await asyncio.to_thread(download_video, url, tmp)
            if not path or os.path.getsize(path) > MAX_SIZE:
                await status.edit_text(t(uid, "video_not_found"))
                return

            token = uuid.uuid4().hex[:10]
            URL_CACHE[token] = url
            kb = InlineKeyboardBuilder()
            kb.button(text=t(uid, "btn_find_song"), callback_data=f"vaudio:{token}")
            kb.button(text=t(uid, "btn_raw_audio"), callback_data=f"vraw:{token}")
            kb.adjust(1)

            await message.answer_video(
                FSInputFile(path),
                caption=t(uid, "video_caption"),
                reply_markup=kb.as_markup(),
            )
        await status.delete()
    except Exception as e:
        await status.edit_text(t(uid, "error", err=str(e)[:300]))


# --- tugma: videodagi musiqani aniqlash ---
@router.callback_query(F.data.startswith("vaudio:"))
async def cb_video_find(call: CallbackQuery):
    uid = call.message.chat.id
    url = URL_CACHE.get(call.data.split(":", 1)[1])
    if not url:
        await call.answer(t(uid, "button_expired"), show_alert=True)
        return
    await call.answer(t(uid, "identifying_toast"))
    status = await call.message.answer(t(uid, "identifying"))
    try:
        with tempfile.TemporaryDirectory() as tmp:
            path, _ = await asyncio.to_thread(download_audio_url, url, tmp)
            if not path:
                await status.edit_text(t(uid, "audio_extract_fail"))
                return
            await identify_and_show(status, path)
    except ImportError:
        await status.edit_text(t(uid, "shazam_missing"))
    except Exception as e:
        await status.edit_text(t(uid, "error", err=str(e)[:300]))


# --- tugma: videodagi ovozning o'zini olish ---
@router.callback_query(F.data.startswith("vraw:"))
async def cb_video_raw(call: CallbackQuery):
    uid = call.message.chat.id
    url = URL_CACHE.get(call.data.split(":", 1)[1])
    if not url:
        await call.answer(t(uid, "button_expired"), show_alert=True)
        return
    await call.answer(t(uid, "raw_toast"))
    status = await call.message.answer(t(uid, "raw_loading"))
    try:
        with tempfile.TemporaryDirectory() as tmp:
            path, title = await asyncio.to_thread(download_audio_url, url, tmp)
            if not path or os.path.getsize(path) > MAX_SIZE:
                await status.edit_text(t(uid, "raw_fail"))
                return
            await call.message.answer_audio(FSInputFile(path), title=title)
        await status.delete()
    except Exception as e:
        await status.edit_text(t(uid, "error", err=str(e)[:300]))
