import asyncio
import tempfile
from pathlib import Path

from aiogram import F, Router
from aiogram.types import FSInputFile, Message

from texts import t

router = Router()
TG_DOWNLOAD_LIMIT = 20 * 1024 * 1024

_BG_SESSION = None


def remove_background(src: str, dst: str):
    """rembg orqali rasmning orqa fonini olib tashlaydi (PNG saqlaydi)."""
    global _BG_SESSION
    from PIL import Image
    from rembg import new_session, remove

    if _BG_SESSION is None:
        _BG_SESSION = new_session("u2netp")  # yengil model
    img = Image.open(src).convert("RGB")
    img.thumbnail((1024, 1024))  # xotirani tejash uchun rasmni kichraytiramiz
    out = remove(img, session=_BG_SESSION)
    out.save(dst, "PNG")


async def process_image(message: Message, file_obj):
    uid = message.chat.id
    if (file_obj.file_size or 0) > TG_DOWNLOAD_LIMIT:
        await message.answer(t(uid, "image_too_big"))
        return
    status = await message.answer(t(uid, "image_processing"))
    try:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "input"
            dst = Path(tmp) / "output.png"
            await message.bot.download(file_obj, destination=src)
            await asyncio.to_thread(remove_background, str(src), str(dst))
            await message.answer_document(
                FSInputFile(dst, filename="no_background.png"),
                caption=t(uid, "image_done"),
            )
        await status.delete()
    except ImportError:
        await status.edit_text(t(uid, "rembg_missing"))
    except Exception as e:
        await status.edit_text(t(uid, "error", err=str(e)[:300]))


@router.message(F.photo)
async def handle_photo(message: Message):
    await process_image(message, message.photo[-1])


@router.message(F.document)
async def handle_document(message: Message):
    doc = message.document
    if not (doc.mime_type or "").startswith("image/"):
        await message.answer(t(message.chat.id, "only_images"))
        return
    await process_image(message, doc)
