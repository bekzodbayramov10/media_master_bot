import json
from pathlib import Path

LANGS = {
    "uz": "🇺🇿 O'zbekcha",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
}
DEFAULT_LANG = "uz"

# Tanlangan tillar shu faylda saqlanadi (foydalanuvchi id -> til kodi)
_STORE = Path(__file__).resolve().parent / "users.json"
try:
    _USER_LANG = json.loads(_STORE.read_text(encoding="utf-8"))
except Exception:
    _USER_LANG = {}


def get_lang(chat_id):
    """Foydalanuvchi tilini qaytaradi, tanlanmagan bo'lsa None."""
    return _USER_LANG.get(str(chat_id))


def set_lang(chat_id, code):
    _USER_LANG[str(chat_id)] = code
    try:
        _STORE.write_text(json.dumps(_USER_LANG), encoding="utf-8")
    except Exception:
        pass


def t(chat_id, key, **kw):
    """Matnni foydalanuvchi tilida qaytaradi."""
    lang = get_lang(chat_id) or DEFAULT_LANG
    text = TEXTS.get(lang, {}).get(key) or TEXTS[DEFAULT_LANG][key]
    return text.format(**kw) if kw else text


def variants(key):
    """Bir kalitning barcha tillardagi matnlari (menyu tugmalarini tanish uchun)."""
    return [TEXTS[lang][key] for lang in TEXTS]


TEXTS = {
    "uz": {
        "btn_video": "🎬 Video yuklash",
        "btn_music": "🎵 Musiqa qidirish",
        "btn_voice": "🎤 Ovozdan musiqa topish",
        "btn_image": "🖼 Rasm orqa fonini o'chirish",
        "btn_lang": "🌐 Til",
        "placeholder": "Havola, qo'shiq nomi yoki rasm yuboring",
        "choose_lang": "🌐 Tilni tanlang / Выберите язык / Choose language",
        "lang_set": "✅ Til tanlandi: O'zbekcha",
        "welcome": "Assalomu alaykum! MediaMaster botiga xush kelibsiz.\n\nPastdagi tugmalardan birini tanlang 👇",
        "menu_title": "Menyu 👇",
        "help": (
            "🎬 Video: havolani yuboring (YouTube, TikTok, Instagram...)\n"
            "🎵 Musiqa: qo'shiq nomi yoki ijrochisini yozing\n"
            "🎤 Ovozdan topish: ovozli xabar, audio yoki video yuboring\n"
            "🖼 Rasm: rasmni yuboring, orqa fonini olib tashlayman\n"
            "🌐 Til: /language\n\n"
            "Menyuni qaytarish: /menu"
        ),
        "hint_video": "🎬 Video havolasini yuboring (YouTube, TikTok, Instagram...).\nVideo kelgach, ostidagi tugma orqali undagi qo'shiqni topishingiz mumkin.",
        "hint_music": "🎵 Qo'shiq nomi yoki ijrochisini yozing.\nMasalan: Rauf Faik",
        "hint_voice": "🎤 Ovozli xabar, audio yoki video yuboring.\nMusiqani aniqlab, to'liq variantlarini topib beraman.",
        "hint_image": "🖼 Rasmni yuboring, orqa fonini olib tashlayman.\nNatija shaffof fonli PNG fayl bo'lib keladi.",
        "video_loading": "⏳ Video yuklanmoqda...",
        "video_not_found": "Video topilmadi yoki 50 MB dan katta.",
        "video_caption": "@media_master_bot orqali yuklab olindi 🚀",
        "btn_find_song": "📥 Qo'shiqni yuklab olish",
        "btn_raw_audio": "🔊 Videodagi ovozni olish",
        "error": "Xatolik: {err}",
        "button_expired": "Tugma eskirgan, havolani qayta yuboring.",
        "identifying": "🎧 Musiqa aniqlanmoqda...",
        "identifying_toast": "Musiqa aniqlanmoqda...",
        "audio_extract_fail": "Videodan ovoz olib bo'lmadi.",
        "not_recognized": "Musiqa aniqlanmadi. Qo'shiq nomini o'zingiz yozib qidirishingiz mumkin.",
        "recognized_no_results": "Aniqlandi: {query}\nLekin variantlar topilmadi.",
        "shazam_missing": "Shazam kutubxonasi o'rnatilmagan.",
        "raw_loading": "⏳ Ovoz yuklanmoqda...",
        "raw_toast": "Ovoz yuklanmoqda...",
        "raw_fail": "Ovoz topilmadi yoki 50 MB dan katta.",
        "searching": "🔎 Qidirilmoqda: {query}",
        "nothing_found": "Hech narsa topilmadi.",
        "search_expired": "Qidiruv eskirgan, qayta yozing.",
        "downloading": "⏳ Yuklanmoqda: {title}",
        "loading_toast": "Yuklanmoqda...",
        "music_fail": "Musiqa topilmadi yoki 50 MB dan katta.",
        "file_too_big": "Fayl 20 MB dan katta. Qisqaroq qismini yuboring.",
        "image_too_big": "Rasm 20 MB dan katta.",
        "image_processing": "🖼 Orqa fon olib tashlanmoqda...\n(birinchi marta model yuklanadi, 1-2 daqiqa ketishi mumkin)",
        "image_done": "✅ Orqa fon olib tashlandi (PNG, shaffof fon)",
        "rembg_missing": "rembg kutubxonasi o'rnatilmagan.",
        "only_images": "Faqat rasm yuboring (JPG yoki PNG).",
    },
    "ru": {
        "btn_video": "🎬 Скачать видео",
        "btn_music": "🎵 Поиск музыки",
        "btn_voice": "🎤 Музыка по голосу",
        "btn_image": "🖼 Удалить фон с фото",
        "btn_lang": "🌐 Язык",
        "placeholder": "Отправьте ссылку, название песни или фото",
        "choose_lang": "🌐 Tilni tanlang / Выберите язык / Choose language",
        "lang_set": "✅ Язык выбран: Русский",
        "welcome": "Здравствуйте! Добро пожаловать в MediaMaster.\n\nВыберите кнопку ниже 👇",
        "menu_title": "Меню 👇",
        "help": (
            "🎬 Видео: отправьте ссылку (YouTube, TikTok, Instagram...)\n"
            "🎵 Музыка: напишите название песни или исполнителя\n"
            "🎤 Поиск по звуку: отправьте голосовое, аудио или видео\n"
            "🖼 Фото: отправьте фото, я уберу фон\n"
            "🌐 Язык: /language\n\n"
            "Вернуть меню: /menu"
        ),
        "hint_video": "🎬 Отправьте ссылку на видео (YouTube, TikTok, Instagram...).\nКогда видео придёт, кнопка под ним поможет найти песню.",
        "hint_music": "🎵 Напишите название песни или исполнителя.\nНапример: Rauf Faik",
        "hint_voice": "🎤 Отправьте голосовое сообщение, аудио или видео.\nЯ определю музыку и найду полные версии.",
        "hint_image": "🖼 Отправьте фото, я уберу фон.\nРезультат придёт файлом PNG с прозрачным фоном.",
        "video_loading": "⏳ Загружаю видео...",
        "video_not_found": "Видео не найдено или больше 50 МБ.",
        "video_caption": "Скачано через @media_master_bot 🚀",
        "btn_find_song": "📥 Найти песню",
        "btn_raw_audio": "🔊 Звук из видео",
        "error": "Ошибка: {err}",
        "button_expired": "Кнопка устарела, отправьте ссылку снова.",
        "identifying": "🎧 Определяю музыку...",
        "identifying_toast": "Определяю музыку...",
        "audio_extract_fail": "Не удалось извлечь звук из видео.",
        "not_recognized": "Музыку определить не удалось. Вы можете написать название песни сами.",
        "recognized_no_results": "Определено: {query}\nНо варианты не найдены.",
        "shazam_missing": "Библиотека Shazam не установлена.",
        "raw_loading": "⏳ Загружаю звук...",
        "raw_toast": "Загружаю звук...",
        "raw_fail": "Звук не найден или больше 50 МБ.",
        "searching": "🔎 Ищу: {query}",
        "nothing_found": "Ничего не найдено.",
        "search_expired": "Поиск устарел, напишите запрос заново.",
        "downloading": "⏳ Загружаю: {title}",
        "loading_toast": "Загружаю...",
        "music_fail": "Музыка не найдена или больше 50 МБ.",
        "file_too_big": "Файл больше 20 МБ. Отправьте часть покороче.",
        "image_too_big": "Фото больше 20 МБ.",
        "image_processing": "🖼 Убираю фон...\n(в первый раз загружается модель, это может занять 1–2 минуты)",
        "image_done": "✅ Фон удалён (PNG, прозрачный фон)",
        "rembg_missing": "Библиотека rembg не установлена.",
        "only_images": "Отправляйте только изображения (JPG или PNG).",
    },
    "en": {
        "btn_video": "🎬 Download video",
        "btn_music": "🎵 Search music",
        "btn_voice": "🎤 Find music by audio",
        "btn_image": "🖼 Remove photo background",
        "btn_lang": "🌐 Language",
        "placeholder": "Send a link, a song name or a photo",
        "choose_lang": "🌐 Tilni tanlang / Выберите язык / Choose language",
        "lang_set": "✅ Language set: English",
        "welcome": "Hello! Welcome to MediaMaster.\n\nChoose a button below 👇",
        "menu_title": "Menu 👇",
        "help": (
            "🎬 Video: send a link (YouTube, TikTok, Instagram...)\n"
            "🎵 Music: type a song or artist name\n"
            "🎤 Find by audio: send a voice message, audio or video\n"
            "🖼 Photo: send a photo and I will remove the background\n"
            "🌐 Language: /language\n\n"
            "Show menu: /menu"
        ),
        "hint_video": "🎬 Send a video link (YouTube, TikTok, Instagram...).\nWhen the video arrives, use the button under it to find the song.",
        "hint_music": "🎵 Type a song or artist name.\nFor example: Rauf Faik",
        "hint_voice": "🎤 Send a voice message, audio or video.\nI will identify the music and find full versions.",
        "hint_image": "🖼 Send a photo and I will remove the background.\nThe result comes as a PNG file with a transparent background.",
        "video_loading": "⏳ Downloading video...",
        "video_not_found": "Video not found or larger than 50 MB.",
        "video_caption": "Downloaded via @media_master_bot 🚀",
        "btn_find_song": "📥 Find the song",
        "btn_raw_audio": "🔊 Audio from video",
        "error": "Error: {err}",
        "button_expired": "This button has expired, please send the link again.",
        "identifying": "🎧 Identifying the music...",
        "identifying_toast": "Identifying the music...",
        "audio_extract_fail": "Could not extract audio from the video.",
        "not_recognized": "Could not identify the music. You can type the song name to search.",
        "recognized_no_results": "Identified: {query}\nBut no results were found.",
        "shazam_missing": "The Shazam library is not installed.",
        "raw_loading": "⏳ Downloading audio...",
        "raw_toast": "Downloading audio...",
        "raw_fail": "Audio not found or larger than 50 MB.",
        "searching": "🔎 Searching: {query}",
        "nothing_found": "Nothing found.",
        "search_expired": "This search has expired, please type it again.",
        "downloading": "⏳ Downloading: {title}",
        "loading_toast": "Downloading...",
        "music_fail": "Music not found or larger than 50 MB.",
        "file_too_big": "The file is larger than 20 MB. Please send a shorter clip.",
        "image_too_big": "The image is larger than 20 MB.",
        "image_processing": "🖼 Removing the background...\n(the model loads the first time, it can take 1-2 minutes)",
        "image_done": "✅ Background removed (PNG, transparent)",
        "rembg_missing": "The rembg library is not installed.",
        "only_images": "Please send images only (JPG or PNG).",
    },
}
