import asyncio
import glob
import math
import re
from pathlib import Path

import yt_dlp
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- .env o'qish (dotenv'siz) ---
ENV_PATH = Path(__file__).resolve().parent / ".env"
import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if ENV_PATH.exists():
    for line in ENV_PATH.read_text(encoding="utf-8-sig").splitlines():
        if line.startswith("BOT_TOKEN="):
            BOT_TOKEN = line.split("=", 1)[1].strip()

MAX_SIZE = 50 * 1024 * 1024  # Telegram bot yuklash limiti: 50 MB
PAGE_SIZE = 10
URL_RE = re.compile(r"https?://\S+")

# (chat_id, message_id) -> {"query": str, "results": list}
SEARCH_CACHE = {}
# qisqa token -> video havolasi
URL_CACHE = {}


def download_audio_url(url: str, outdir: str):
    """Havoladan audioni mp3 qilib yuklaydi. (fayl yo'li, nomi) qaytaradi."""
    opts = {
        "outtmpl": f"{outdir}/%(id)s.%(ext)s",
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "no_color": True,
        "max_filesize": MAX_SIZE,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
    files = glob.glob(f"{outdir}/*.mp3")
    title = (info or {}).get("title") or "Musiqa"
    return (files[0] if files else None), title


def search_music(query: str):
    opts = {
        "quiet": True,
        "no_color": True,
        "extract_flat": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"ytsearch30:{query}", download=False)
    results = []
    for e in info.get("entries", []):
        if e and e.get("id"):
            results.append(
                {
                    "id": e["id"],
                    "title": e.get("title") or "Nomsiz",
                    "duration": e.get("duration"),
                }
            )
    return results


async def recognize_song(path: str):
    """Shazam orqali musiqani aniqlaydi. (ijrochi, nomi) yoki None qaytaradi."""
    from shazamio import Shazam

    shazam = Shazam()
    if hasattr(shazam, "recognize"):
        out = await shazam.recognize(path)
    else:
        out = await shazam.recognize_song(path)
    track = (out or {}).get("track")
    if not track:
        return None
    return track.get("subtitle", ""), track.get("title", "")


def fmt_duration(sec):
    if not sec:
        return ""
    sec = int(sec)
    return f"{sec // 60}:{sec % 60:02d}"


def render_page(query: str, results: list, page: int):
    total_pages = math.ceil(len(results) / PAGE_SIZE)
    start = page * PAGE_SIZE
    chunk = results[start : start + PAGE_SIZE]

    lines = [f"🔍 {query}", ""]
    for i, r in enumerate(chunk, start=start + 1):
        lines.append(f"{i}. {r['title']} {fmt_duration(r['duration'])}".strip())
    text = "\n".join(lines)

    kb = InlineKeyboardBuilder()
    for i in range(start, start + len(chunk)):
        kb.button(text=str(i + 1), callback_data=f"pick:{i}")
    kb.adjust(5)

    nav = InlineKeyboardBuilder()
    if total_pages > 1:
        nav.button(text="⬅️", callback_data=f"page:{(page - 1) % total_pages}")
    nav.button(text="❌", callback_data="close")
    if total_pages > 1:
        nav.button(text="➡️", callback_data=f"page:{(page + 1) % total_pages}")
    kb.attach(nav)
    return text, kb.as_markup()


async def identify_and_show(status: Message, path: str):
    """Fayldagi musiqani aniqlaydi va 10 variantli ro'yxatni ko'rsatadi."""
    found = await recognize_song(path)
    if not found:
        await status.edit_text(
            "Musiqa aniqlanmadi. Qo'shiq nomini o'zingiz yozib qidirishingiz mumkin."
        )
        return
    artist, title = found
    query = f"{artist} - {title}".strip(" -")
    results = await asyncio.to_thread(search_music, query)
    if not results:
        await status.edit_text(f"Aniqlandi: {query}\nLekin variantlar topilmadi.")
        return
    SEARCH_CACHE[(status.chat.id, status.message_id)] = {
        "query": query,
        "results": results,
    }
    text, kb = render_page(query, results, 0)
    await status.edit_text(text, reply_markup=kb)
