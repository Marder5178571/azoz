import json
import logging
import os
from typing import Dict, Optional, Any, Set, List

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# =========================================================
# НАСТРОЙКИ (ОБЯЗАТЕЛЬНО ЗАПОЛНИТЬ)
# =========================================================
BOT_TOKEN = "8355075682:AAELU8BHiV240FqyOB9H_-3KFqbxoMm-MAk"  # один токен прямо здесь

# КАНАЛ:
# ВАЖНО: ссылка вида https://t.me/+xxxx — это НЕ chat_id.
# Нужен @username канала или числовой id -100xxxxxxxxxx
CHANNEL_CHAT_ID = -1003629048716
CHANNEL_URL = "https://t.me/Pakhtakor_pro_challenge"  # ссылка для кнопки на канал

# Владелец (OWNER): может добавлять/удалять админов
OWNER_USER_ID = 1266601946  # ваш user_id числом (узнать: /myid)

LEVELS = [1, 2, 3, 4]
TASKS = [1, 2, 3]

DATA_FILE = "levels_data.json"
ADMINS_FILE = "admins.json"
USERS_FILE = "users.json"  # регистрация пользователей: имя+фамилия, язык

# =========================================================
# СТИКЕРЫ
# Получить sticker file_id: отправьте боту стикер и напишите /stickerid
# =========================================================
STICKERS = {
    "DEFAULT": "PASTE_STICKER_FILE_ID_HERE",  # <-- сюда вставьте file_id стикера
    "WELCOME": "",
    "OK": "",
    "ERROR": "",
    "RULES": "",
    "ADMIN": "",
    "PANEL": "",
}

# =========================================================
# ЛОГИ
# =========================================================
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("pakhtakor_pro")

# =========================================================
# ЯЗЫКИ / КНОПКИ (ЭМОДЗИ-НАВИГАЦИЯ)
# =========================================================
LANGS = ["ru", "uz", "en"]

BTN = {
    # выбор языка
    "LANG_RU": {"ru": "🇷🇺 Русский", "uz": "🇷🇺 Русский", "en": "🇷🇺 Русский"},
    "LANG_UZ": {"ru": "🇺🇿 O‘zbekcha", "uz": "🇺🇿 O‘zbekcha", "en": "🇺🇿 O‘zbekcha"},
    "LANG_EN": {"ru": "🇬🇧 English", "uz": "🇬🇧 English", "en": "🇬🇧 English"},

    # смена языка (всегда)
    "LANG_MENU": {"ru": "🌐 Язык", "uz": "🌐 Til", "en": "🌐 Language"},

    # панели
    "PANEL_PLAYER": {"ru": "🎮 Игрок", "uz": "🎮 O‘yinchi", "en": "🎮 Player"},
    "PANEL_ADMIN": {"ru": "🛠 Админ", "uz": "🛠 Admin", "en": "🛠 Admin"},

    # навигация
    "HOME": {"ru": "🏠 Главное меню", "uz": "🏠 Asosiy menyu", "en": "🏠 Main menu"},
    "BACK_LEVELS": {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "en": "⬅️ Back"},
    "CANCEL": {"ru": "❌ Отмена", "uz": "❌ Bekor", "en": "❌ Cancel"},

    # общие
    "RULES": {"ru": "📌 Правила", "uz": "📌 Qoidalar", "en": "📌 Rules"},
    "STATUS": {"ru": "📊 Статус", "uz": "📊 Holat", "en": "📊 Status"},
    "CHANNEL_BTN": {"ru": "📣 Канал", "uz": "📣 Kanal", "en": "📣 Channel"},
    "OPEN_CHANNEL": {"ru": "📣 Перейти в канал", "uz": "📣 Kanalga o‘tish", "en": "📣 Open channel"},

    # OWNER: управление админами кнопками
    "OWNER_ADD_ADMIN": {"ru": "➕ Добавить админа", "uz": "➕ Admin qo‘shish", "en": "➕ Add admin"},
    "OWNER_DEL_ADMIN": {"ru": "➖ Удалить админа", "uz": "➖ Adminni o‘chirish", "en": "➖ Remove admin"},
    "OWNER_LIST_ADMINS": {"ru": "👥 Список админов", "uz": "👥 Adminlar ro‘yxati", "en": "👥 Admin list"},

    # уровни
    "LEVEL_1": {"ru": "1️⃣ Уровень 1", "uz": "1️⃣ Daraja 1", "en": "1️⃣ Level 1"},
    "LEVEL_2": {"ru": "2️⃣ Уровень 2", "uz": "2️⃣ Daraja 2", "en": "2️⃣ Level 2"},
    "LEVEL_3": {"ru": "3️⃣ Уровень 3", "uz": "3️⃣ Daraja 3", "en": "3️⃣ Level 3"},
    "LEVEL_4": {"ru": "4️⃣ Уровень 4", "uz": "4️⃣ Daraja 4", "en": "4️⃣ Level 4"},

    # задания
    "TASK_1": {"ru": "🟢 Задание 1", "uz": "🟢 Topshiriq 1", "en": "🟢 Task 1"},
    "TASK_2": {"ru": "🟡 Задание 2", "uz": "🟡 Topshiriq 2", "en": "🟡 Task 2"},
    "TASK_3": {"ru": "🔴 Задание 3", "uz": "🔴 Topshiriq 3", "en": "🔴 Task 3"},
}

TXT = {
    "CHOOSE_LANG": {
        "ru": "🌐 Выберите язык / Tilni tanlang / Choose language:",
        "uz": "🌐 Tilni tanlang / Выберите язык / Choose language:",
        "en": "🌐 Choose language / Выберите язык / Tilni tanlang:",
    },

    # Приветствие — отправляется ПОСЛЕ выбора языка
    "GREET_AFTER_LANG": {
        "ru": "Добро пожаловать в Pakhtakor Pro bot — официальный бот для челленджа.",
        "uz": "Pakhtakor Pro bot’ga xush kelibsiz — challenge uchun rasmiy bot.",
        "en": "Welcome to Pakhtakor Pro bot — the official bot for the challenge.",
    },

    # Регистрация: имя+фамилия
    "ASK_REGISTER_NAME": {
        "ru": "📝 Регистрация\nОтправьте *Имя и Фамилию* одним сообщением.\nПример: Иван Петров",
        "uz": "📝 Ro‘yxatdan o‘tish\n*Ism va Familiya*ni bitta xabar qilib yuboring.\nMisol: Ivan Petrov",
        "en": "📝 Registration\nSend your *First name and Last name* in one message.\nExample: Ivan Petrov",
    },
    "REGISTER_SAVED": {
        "ru": "✅ Спасибо! Регистрация сохранена: {name}",
        "uz": "✅ Rahmat! Ro‘yxatdan o‘tish saqlandi: {name}",
        "en": "✅ Thank you! Registration saved: {name}",
    },
    "REGISTER_INVALID": {
        "ru": "⚠️ Пожалуйста, отправьте *Имя и Фамилию* (2 слова или больше).",
        "uz": "⚠️ Iltimos, *Ism va Familiya* yuboring (kamida 2 ta so‘z).",
        "en": "⚠️ Please send *First name and Last name* (2 words or more).",
    },
    "NEED_REGISTER_FIRST": {
        "ru": "⚠️ Сначала зарегистрируйтесь: отправьте Имя и Фамилию.",
        "uz": "⚠️ Avval ro‘yxatdan o‘ting: Ism va Familiya yuboring.",
        "en": "⚠️ Please register first: send First name and Last name.",
    },

    "CHOOSE_PANEL_ADMIN": {"ru": "🧭 Выберите панель:", "uz": "🧭 Panelni tanlang:", "en": "🧭 Choose a panel:"},
    "PLAYER_START": {"ru": "🎮 Выбери уровень кнопками ниже.", "uz": "🎮 Pastdagi tugmalar orqali darajani tanlang.", "en": "🎮 Choose a level using the buttons below."},

    "RULES_TEXT": {
        "ru": "📌 Правила:\n1) Выбери уровень (1–4)\n2) Выбери задание (1–3)\n3) Получи видео + описание\n4) Запиши видео-ответ и отправь сюда\n5) Бот отправит твой ответ в канал",
        "uz": "📌 Qoidalar:\n1) Darajani tanlang (1–4)\n2) Topshiriqni tanlang (1–3)\n3) Video + tavsifni oling\n4) Video-javobni yozib shu yerga yuboring\n5) Bot javobingizni kanalga yuboradi",
        "en": "📌 Rules:\n1) Choose a level (1–4)\n2) Choose a task (1–3)\n3) Receive video + description\n4) Record your response and send it here\n5) The bot posts it to the channel",
    },
    "LEVEL_CHOSEN": {"ru": "✅ Уровень {lvl} выбран. Теперь выбери задание.", "uz": "✅ Daraja {lvl} tanlandi. Endi topshiriqni tanlang.", "en": "✅ Level {lvl} selected. Now choose a task."},
    "NEED_LEVEL_FIRST": {"ru": "⚠️ Сначала выбери уровень.", "uz": "⚠️ Avval darajani tanlang.", "en": "⚠️ Choose a level first."},
    "NO_CONTENT": {"ru": "⏳ Уровень {lvl}, задание {task}: контента пока нет.", "uz": "⏳ Daraja {lvl}, topshiriq {task}: hozircha kontent yo‘q.", "en": "⏳ Level {lvl}, task {task}: no content yet."},
    "SEND_RESPONSE": {"ru": "📤 Теперь отправь видео-ответ сюда — бот отправит его в канал.", "uz": "📤 Endi video-javobingizni yuboring — bot uni kanalga yuboradi.", "en": "📤 Now send your video response — the bot will post it to the channel."},
    "NEED_TASK_SELECTED_FOR_VIDEO": {"ru": "⚠️ Сначала выбери уровень и задание, потом отправляй видео-ответ.", "uz": "⚠️ Avval daraja va topshiriqni tanlang, keyin video yuboring.", "en": "⚠️ Choose level and task first, then send your video."},
    "SENT_TO_CHANNEL_OK": {"ru": "✅ Принял. Видео отправлено в канал.", "uz": "✅ Qabul qilindi. Video kanalga yuborildi.", "en": "✅ Received. Posted to the channel."},
    "CANT_POST_TO_CHANNEL": {
        "ru": "❌ Не смог отправить в канал.\nПроверь:\n1) Бот админ в канале\n2) CHANNEL_CHAT_ID верный\n3) Есть право Post messages",
        "uz": "❌ Kanalga yubora olmadim.\nTekshiring:\n1) Bot kanal adminimi\n2) CHANNEL_CHAT_ID to‘g‘rimi\n3) Post messages ruxsati bormi",
        "en": "❌ Could not post to the channel.\nCheck:\n1) Bot is channel admin\n2) CHANNEL_CHAT_ID is correct\n3) Post messages permission",
    },

    "ADMIN_OPENED": {"ru": "🛠 Админ-панель открыта. Выбери уровень.", "uz": "🛠 Admin paneli ochildi. Darajani tanlang.", "en": "🛠 Admin panel opened. Choose a level."},
    "PLAYER_OPENED": {"ru": "🎮 Игровая панель открыта. Выбери уровень.", "uz": "🎮 O‘yinchi paneli ochildi. Darajani tanlang.", "en": "🎮 Player panel opened. Choose a level."},
    "ADMIN_PICK_TASK": {"ru": "🛠 Уровень {lvl} выбран. Теперь выбери задание.", "uz": "🛠 Daraja {lvl} tanlandi. Endi topshiriqni tanlang.", "en": "🛠 Level {lvl} selected. Now choose a task."},
    "ADMIN_SEND_VIDEO": {"ru": "🎬 Настройка: уровень {lvl}, задание {task}.\nОтправь ВИДЕО для задания.", "uz": "🎬 Sozlash: daraja {lvl}, topshiriq {task}.\nTopshiriq videosini yuboring.", "en": "🎬 Setup: level {lvl}, task {task}.\nSend the TASK VIDEO."},
    "ADMIN_GOT_VIDEO_SEND_DESC": {"ru": "✅ Видео принято.\nТеперь отправь ОПИСАНИЕ текстом.", "uz": "✅ Video qabul qilindi.\nEndi tavsifni matn bilan yuboring.", "en": "✅ Video received.\nNow send the DESCRIPTION as text."},
    "ADMIN_SAVED": {"ru": "✅ Сохранено: уровень {lvl}, задание {task}.", "uz": "✅ Saqlandi: daraja {lvl}, topshiriq {task}.", "en": "✅ Saved: level {lvl}, task {task}."},

    "STATUS_HEADER": {"ru": "📊 Статус (в каждом уровне 3 задания):", "uz": "📊 Holat (har darajada 3 topshiriq):", "en": "📊 Status (3 tasks per level):"},
    "CANCELLED": {"ru": "✅ Отменено.", "uz": "✅ Bekor qilindi.", "en": "✅ Cancelled."},
    "ACCESS_DENIED": {"ru": "⛔ Доступ запрещён.", "uz": "⛔ Kirish taqiqlangan.", "en": "⛔ Access denied."},
    "ADMIN_VIDEO_WRONG_PANEL": {
        "ru": "⚠️ Ты в 🛠 Админ.\nЧтобы загрузить видео задания: выбери уровень → задание.\nЧтобы отправить видео как игрок — перейди в 🎮 Игрок.",
        "uz": "⚠️ Siz 🛠 Admin panelidasiz.\nTopshiriq videosi uchun: daraja → topshiriq.\nO‘yinchi sifatida video yuborish uchun 🎮 O‘yinchi ga o‘ting.",
        "en": "⚠️ You are in 🛠 Admin panel.\nTo set a task video: level → task.\nTo send a player response, switch to 🎮 Player.",
    },

    # OWNER UI
    "OWNER_ADD_PROMPT": {
        "ru": "➕ Отправь user_id нового админа.\nПодсказка: человек может написать боту /myid и прислать тебе число.",
        "uz": "➕ Yangi admin user_id raqamini yuboring.\nMaslahat: odam botga /myid yozib, raqamni sizga yuborsin.",
        "en": "➕ Send the new admin user_id.\nTip: ask them to send /myid to the bot and forward you the number.",
    },
    "OWNER_DEL_PROMPT": {"ru": "➖ Отправь user_id админа, которого нужно удалить.", "uz": "➖ O‘chiriladigan admin user_id raqamini yuboring.", "en": "➖ Send the admin user_id to remove."},
    "OWNER_ADDED": {"ru": "✅ Добавлен админ: {uid}", "uz": "✅ Admin qo‘shildi: {uid}", "en": "✅ Admin added: {uid}"},
    "OWNER_REMOVED": {"ru": "✅ Удалён админ: {uid}", "uz": "✅ Admin o‘chirildi: {uid}", "en": "✅ Admin removed: {uid}"},
    "OWNER_CANNOT_REMOVE_SELF": {"ru": "⚠️ Нельзя удалить владельца (OWNER).", "uz": "⚠️ Egani (OWNER) o‘chirish mumkin emas.", "en": "⚠️ Owner cannot be removed."},
    "OWNER_BAD_ID": {"ru": "❌ Неверный user_id. Нужно число, например: 123456789", "uz": "❌ Noto‘g‘ri user_id. Raqam bo‘lishi kerak, masalan: 123456789", "en": "❌ Invalid user_id. Must be a number, e.g.: 123456789"},
}

# =========================================================
# ХРАНЕНИЕ ПОЛЬЗОВАТЕЛЕЙ (регистрация + язык)
# =========================================================
def _load_users() -> Dict[str, Dict[str, str]]:
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        logger.exception("Failed to load users: %s", e)
        return {}


def _save_users(users: Dict[str, Dict[str, str]]) -> None:
    tmp = USERS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    os.replace(tmp, USERS_FILE)


USERS: Dict[str, Dict[str, str]] = _load_users()


def get_registered_name(user_id: int) -> str:
    rec = USERS.get(str(user_id), {})
    return str(rec.get("name", "")).strip()


def set_registered_name(user_id: int, name: str) -> None:
    uid = str(user_id)
    if uid not in USERS:
        USERS[uid] = {}
    USERS[uid]["name"] = name.strip()
    _save_users(USERS)


def get_saved_lang(user_id: int) -> Optional[str]:
    rec = USERS.get(str(user_id), {})
    lang = str(rec.get("lang", "")).strip()
    return lang if lang in LANGS else None


def set_saved_lang(user_id: int, lang: str) -> None:
    uid = str(user_id)
    if uid not in USERS:
        USERS[uid] = {}
    USERS[uid]["lang"] = lang
    _save_users(USERS)


def is_registered(user_id: int) -> bool:
    return bool(get_registered_name(user_id))


# =========================================================
# УТИЛИТЫ: ЯЗЫК / КНОПКИ / СТИКЕРЫ / ОТВЕТЫ
# =========================================================
def get_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    lang = context.user_data.get("lang", "ru")
    return lang if lang in LANGS else "ru"


def set_lang(context: ContextTypes.DEFAULT_TYPE, lang: str) -> None:
    context.user_data["lang"] = lang


def t(context: ContextTypes.DEFAULT_TYPE, key: str, **kwargs) -> str:
    lang = get_lang(context)
    text = TXT.get(key, {}).get(lang) or TXT.get(key, {}).get("ru") or key
    return text.format(**kwargs)


def all_btn_texts(btn_key: str) -> List[str]:
    d = BTN.get(btn_key, {})
    return [str(v).strip().lower() for v in d.values() if isinstance(v, str)]


def is_btn(text: str, btn_key: str) -> bool:
    return text.strip().lower() in all_btn_texts(btn_key)


def _pick_sticker(key: str) -> str:
    s = (STICKERS.get(key) or "").strip()
    if not s:
        s = (STICKERS.get("DEFAULT") or "").strip()
    if not s or "PASTE_STICKER_FILE_ID_HERE" in s:
        return ""
    return s


async def send_sticker_safe(context: ContextTypes.DEFAULT_TYPE, chat_id: int, key: str) -> None:
    sticker_id = _pick_sticker(key)
    if not sticker_id:
        return
    try:
        await context.bot.send_sticker(chat_id=chat_id, sticker=sticker_id)
    except Exception as e:
        logger.warning("Failed to send sticker (%s): %s", key, e)


async def say(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    reply_markup=None,
    sticker_key: str = "DEFAULT",
) -> None:
    if update.effective_chat:
        await send_sticker_safe(context, update.effective_chat.id, sticker_key)
    if update.message:
        parse_mode = "Markdown" if ("*" in text) else None
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)


# =========================================================
# АДМИНЫ (сохранение)
# =========================================================
def load_admins() -> Set[int]:
    admins = {OWNER_USER_ID}
    if os.path.exists(ADMINS_FILE):
        try:
            with open(ADMINS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                for x in data:
                    if isinstance(x, int):
                        admins.add(x)
                    elif isinstance(x, str) and x.isdigit():
                        admins.add(int(x))
        except Exception as e:
            logger.exception("Failed to load admins: %s", e)
    return admins


def save_admins(admins: Set[int]) -> None:
    tmp = ADMINS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(sorted(list(admins)), f, ensure_ascii=False, indent=2)
    os.replace(tmp, ADMINS_FILE)


ADMIN_IDS: Set[int] = load_admins()


def is_owner(update: Update) -> bool:
    return update.effective_user is not None and update.effective_user.id == OWNER_USER_ID


def is_admin(update: Update) -> bool:
    return update.effective_user is not None and update.effective_user.id in ADMIN_IDS


# =========================================================
# ДАННЫЕ УРОВНЕЙ/ЗАДАНИЙ (JSON)
# =========================================================
def load_levels() -> Dict[str, Dict[str, Dict[str, str]]]:
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {}
        out: Dict[str, Dict[str, Dict[str, str]]] = {}
        for lvl_key, lvl_val in data.items():
            if not isinstance(lvl_key, str) or not isinstance(lvl_val, dict):
                continue
            tasks_out: Dict[str, Dict[str, str]] = {}
            for task_key, payload in lvl_val.items():
                if not isinstance(task_key, str) or not isinstance(payload, dict):
                    continue
                video = str(payload.get("video_file_id", "")).strip()
                desc = str(payload.get("description", "")).strip()
                if video or desc:
                    tasks_out[task_key] = {"video_file_id": video, "description": desc}
            if tasks_out:
                out[lvl_key] = tasks_out
        return out
    except Exception as e:
        logger.exception("Failed to load levels: %s", e)
        return {}


def save_levels(data: Dict[str, Dict[str, Dict[str, str]]]) -> None:
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)


LEVEL_DATA: Dict[str, Dict[str, Dict[str, str]]] = load_levels()


def get_payload(level: int, task: int) -> Optional[Dict[str, str]]:
    return LEVEL_DATA.get(str(level), {}).get(str(task))


def set_payload(level: int, task: int, video_file_id: str, description: str) -> None:
    lvl_key = str(level)
    task_key = str(task)
    if lvl_key not in LEVEL_DATA:
        LEVEL_DATA[lvl_key] = {}
    LEVEL_DATA[lvl_key][task_key] = {
        "video_file_id": (video_file_id or "").strip(),
        "description": (description or "").strip(),
    }
    save_levels(LEVEL_DATA)


# =========================================================
# СОСТОЯНИЕ ПОЛЬЗОВАТЕЛЯ
# =========================================================
def panel_get(context: ContextTypes.DEFAULT_TYPE) -> str:
    return str(context.user_data.get("panel", "player"))  # player | admin


def panel_set(context: ContextTypes.DEFAULT_TYPE, value: str) -> None:
    context.user_data["panel"] = value


def player_level_get(context: ContextTypes.DEFAULT_TYPE) -> Optional[int]:
    v = context.user_data.get("player_level")
    return int(v) if isinstance(v, int) else None


def player_level_set(context: ContextTypes.DEFAULT_TYPE, level: Optional[int]) -> None:
    if level is None:
        context.user_data.pop("player_level", None)
    else:
        context.user_data["player_level"] = level


def player_task_get(context: ContextTypes.DEFAULT_TYPE) -> Optional[int]:
    v = context.user_data.get("player_task")
    return int(v) if isinstance(v, int) else None


def player_task_set(context: ContextTypes.DEFAULT_TYPE, task: Optional[int]) -> None:
    if task is None:
        context.user_data.pop("player_task", None)
    else:
        context.user_data["player_task"] = task


def admin_level_get(context: ContextTypes.DEFAULT_TYPE) -> Optional[int]:
    v = context.user_data.get("admin_level")
    return int(v) if isinstance(v, int) else None


def admin_level_set(context: ContextTypes.DEFAULT_TYPE, level: Optional[int]) -> None:
    if level is None:
        context.user_data.pop("admin_level", None)
    else:
        context.user_data["admin_level"] = level


def set_awaiting_registration(context: ContextTypes.DEFAULT_TYPE, value: bool) -> None:
    context.user_data["awaiting_registration"] = bool(value)


def is_awaiting_registration(context: ContextTypes.DEFAULT_TYPE) -> bool:
    return bool(context.user_data.get("awaiting_registration", False))


# =========================================================
# КЛАВИАТУРЫ (ReplyKeyboard под чатом)
# =========================================================
def kb_language() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[BTN["LANG_RU"]["ru"], BTN["LANG_UZ"]["ru"], BTN["LANG_EN"]["ru"]]],
        resize_keyboard=True,
    )


def kb_choose_panel(context: ContextTypes.DEFAULT_TYPE, owner_user: bool) -> ReplyKeyboardMarkup:
    lang = get_lang(context)
    rows = [
        [BTN["PANEL_PLAYER"][lang], BTN["PANEL_ADMIN"][lang]],
        [BTN["CHANNEL_BTN"][lang], BTN["LANG_MENU"][lang]],
        [BTN["HOME"][lang]],
    ]
    if owner_user:
        rows.append([BTN["OWNER_ADD_ADMIN"][lang], BTN["OWNER_LIST_ADMINS"][lang]])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def kb_player_levels(context: ContextTypes.DEFAULT_TYPE, admin_user: bool, owner_user: bool) -> ReplyKeyboardMarkup:
    lang = get_lang(context)
    rows = [
        [BTN["LEVEL_1"][lang], BTN["LEVEL_2"][lang]],
        [BTN["LEVEL_3"][lang], BTN["LEVEL_4"][lang]],
        [BTN["CHANNEL_BTN"][lang], BTN["RULES"][lang]],
        [BTN["LANG_MENU"][lang], BTN["HOME"][lang]],
    ]
    if admin_user:
        rows.append([BTN["PANEL_ADMIN"][lang]])
    if owner_user:
        rows.append([BTN["OWNER_ADD_ADMIN"][lang], BTN["OWNER_LIST_ADMINS"][lang]])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def kb_player_tasks(context: ContextTypes.DEFAULT_TYPE, admin_user: bool, owner_user: bool, level: int) -> ReplyKeyboardMarkup:
    lang = get_lang(context)
    rows = [
        [BTN["TASK_1"][lang], BTN["TASK_2"][lang]],
        [BTN["TASK_3"][lang]],
        [BTN["CHANNEL_BTN"][lang], BTN["RULES"][lang]],
        [BTN["BACK_LEVELS"][lang], BTN["HOME"][lang]],
        [BTN["LANG_MENU"][lang]],
    ]
    if admin_user:
        rows.append([BTN["PANEL_ADMIN"][lang]])
    if owner_user:
        rows.append([BTN["OWNER_ADD_ADMIN"][lang], BTN["OWNER_LIST_ADMINS"][lang]])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def kb_admin_levels(context: ContextTypes.DEFAULT_TYPE, owner_user: bool) -> ReplyKeyboardMarkup:
    lang = get_lang(context)
    rows = [
        [BTN["LEVEL_1"][lang], BTN["LEVEL_2"][lang]],
        [BTN["LEVEL_3"][lang], BTN["LEVEL_4"][lang]],
        [BTN["CHANNEL_BTN"][lang], BTN["STATUS"][lang]],
        [BTN["LANG_MENU"][lang], BTN["HOME"][lang]],
        [BTN["PANEL_PLAYER"][lang]],
    ]
    if owner_user:
        rows.append([BTN["OWNER_ADD_ADMIN"][lang], BTN["OWNER_DEL_ADMIN"][lang]])
        rows.append([BTN["OWNER_LIST_ADMINS"][lang]])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def kb_admin_tasks(context: ContextTypes.DEFAULT_TYPE, owner_user: bool, level: int) -> ReplyKeyboardMarkup:
    lang = get_lang(context)
    rows = [
        [BTN["TASK_1"][lang], BTN["TASK_2"][lang]],
        [BTN["TASK_3"][lang]],
        [BTN["CHANNEL_BTN"][lang], BTN["STATUS"][lang]],
        [BTN["BACK_LEVELS"][lang], BTN["HOME"][lang]],
        [BTN["LANG_MENU"][lang]],
        [BTN["CANCEL"][lang], BTN["PANEL_PLAYER"][lang]],
    ]
    if owner_user:
        rows.append([BTN["OWNER_ADD_ADMIN"][lang], BTN["OWNER_DEL_ADMIN"][lang]])
        rows.append([BTN["OWNER_LIST_ADMINS"][lang]])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def channel_button(context: ContextTypes.DEFAULT_TYPE) -> InlineKeyboardMarkup:
    lang = get_lang(context)
    return InlineKeyboardMarkup([[InlineKeyboardButton(BTN["OPEN_CHANNEL"][lang], url=CHANNEL_URL)]])


# =========================================================
# ПАРСИНГ УРОВНЕЙ/ЗАДАНИЙ ПО КНОПКАМ
# =========================================================
def parse_level(text: str) -> Optional[int]:
    tx = text.strip().lower()
    if tx in all_btn_texts("LEVEL_1"):
        return 1
    if tx in all_btn_texts("LEVEL_2"):
        return 2
    if tx in all_btn_texts("LEVEL_3"):
        return 3
    if tx in all_btn_texts("LEVEL_4"):
        return 4
    return None


def parse_task(text: str) -> Optional[int]:
    tx = text.strip().lower()
    if tx in all_btn_texts("TASK_1"):
        return 1
    if tx in all_btn_texts("TASK_2"):
        return 2
    if tx in all_btn_texts("TASK_3"):
        return 3
    return None


# =========================================================
# Валидация регистрации (Имя Фамилия)
# =========================================================
def normalize_full_name(name: str) -> str:
    return " ".join([w for w in name.strip().split() if w])


def is_valid_full_name(name: str) -> bool:
    name = normalize_full_name(name)
    parts = name.split()
    if len(parts) < 2:
        return False
    for p in parts:
        if len(p) < 2:
            return False
    return True


# =========================================================
# Показать текущее меню
# =========================================================
async def show_current_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    admin_user = is_admin(update)
    owner_user = is_owner(update)
    pnl = panel_get(context) if admin_user else "player"

    if admin_user and pnl == "admin":
        lvl = admin_level_get(context)
        if lvl is None:
            await say(update, context, "OK", reply_markup=kb_admin_levels(context, owner_user=owner_user), sticker_key="ADMIN")
        else:
            await say(update, context, "OK", reply_markup=kb_admin_tasks(context, owner_user=owner_user, level=lvl), sticker_key="ADMIN")
        return

    lvl = player_level_get(context)
    if lvl is None:
        await say(update, context, "OK", reply_markup=kb_player_levels(context, admin_user=admin_user, owner_user=owner_user), sticker_key="PANEL")
    else:
        await say(update, context, "OK", reply_markup=kb_player_tasks(context, admin_user=admin_user, owner_user=owner_user, level=lvl), sticker_key="PANEL")


# =========================================================
# START
# ВАЖНО: теперь приветствие отправляется каждый раз при /start
# =========================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # сброс навигации
    panel_set(context, "player")
    player_level_set(context, None)
    player_task_set(context, None)
    admin_level_set(context, None)
    context.user_data.pop("admin_mode", None)
    context.user_data.pop("owner_mode", None)

    user = update.effective_user
    if not user:
        return

    # восстановим язык из файла, если есть
    saved_lang = get_saved_lang(user.id)
    if saved_lang and "lang" not in context.user_data:
        set_lang(context, saved_lang)

    # 1) Язык ещё не выбран -> просим выбрать
    if "lang" not in context.user_data:
        set_awaiting_registration(context, False)
        await say(update, context, TXT["CHOOSE_LANG"]["ru"], reply_markup=kb_language(), sticker_key="WELCOME")
        return

    # 2) Каждый раз при /start отправляем приветствие на выбранном языке
    await say(
        update,
        context,
        t(context, "GREET_AFTER_LANG"),
        reply_markup=ReplyKeyboardRemove(),
        sticker_key="WELCOME",
    )

    # 3) Если не зарегистрирован — просим регистрацию
    if not is_registered(user.id):
        set_awaiting_registration(context, True)
        await say(update, context, t(context, "ASK_REGISTER_NAME"), reply_markup=ReplyKeyboardRemove(), sticker_key="WELCOME")
        return

    # 4) Если зарегистрирован — показываем кнопку канала и меню
    set_awaiting_registration(context, False)
    await say(update, context, "📣", reply_markup=channel_button(context), sticker_key="OK")

    if is_admin(update):
        await say(update, context, t(context, "CHOOSE_PANEL_ADMIN"), reply_markup=kb_choose_panel(context, owner_user=is_owner(update)), sticker_key="PANEL")
    else:
        await say(update, context, t(context, "PLAYER_START"), reply_markup=kb_player_levels(context, admin_user=False, owner_user=is_owner(update)), sticker_key="PANEL")


async def lang_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await say(update, context, TXT["CHOOSE_LANG"]["ru"], reply_markup=kb_language(), sticker_key="PANEL")


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await say(update, context, f"user_id: {update.effective_user.id}", sticker_key="OK")


async def stickerid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    if msg is None:
        return
    target = msg.reply_to_message if msg.reply_to_message else msg
    if target.sticker:
        await msg.reply_text(f"sticker file_id:\n{target.sticker.file_id}")
    else:
        await msg.reply_text("Отправь мне стикер или ответь на стикер командой /stickerid.")


async def hide(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat:
        await send_sticker_safe(context, update.effective_chat.id, "OK")
    await update.message.reply_text("OK", reply_markup=ReplyKeyboardRemove())


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if is_admin(update):
        context.user_data.pop("admin_mode", None)
    if is_owner(update):
        context.user_data.pop("owner_mode", None)

    set_awaiting_registration(context, False)

    await say(update, context, t(context, "CANCELLED"), sticker_key="OK")
    await show_current_menu(update, context)


# =========================================================
# OWNER (backup команды) + кнопки
# =========================================================
async def owner_list_admins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update):
        await say(update, context, t(context, "ACCESS_DENIED"), sticker_key="ERROR")
        return
    admins_sorted = sorted(list(ADMIN_IDS))
    text = "👥 Admins:\n" + "\n".join(str(x) for x in admins_sorted)
    await say(update, context, text, sticker_key="OK")


def _extract_user_id_from_text(text_raw: str) -> Optional[int]:
    tx = text_raw.strip()
    if tx.isdigit():
        try:
            return int(tx)
        except Exception:
            return None
    return None


async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update):
        await say(update, context, t(context, "ACCESS_DENIED"), sticker_key="ERROR")
        return
    if not context.args or not context.args[0].isdigit():
        await say(update, context, "Usage: /addadmin 123456789", sticker_key="ERROR")
        return
    uid = int(context.args[0])
    ADMIN_IDS.add(uid)
    save_admins(ADMIN_IDS)
    await say(update, context, t(context, "OWNER_ADDED", uid=uid), sticker_key="OK")


async def deladmin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update):
        await say(update, context, t(context, "ACCESS_DENIED"), sticker_key="ERROR")
        return
    if not context.args or not context.args[0].isdigit():
        await say(update, context, "Usage: /deladmin 123456789", sticker_key="ERROR")
        return
    uid = int(context.args[0])
    if uid == OWNER_USER_ID:
        await say(update, context, t(context, "OWNER_CANNOT_REMOVE_SELF"), sticker_key="ERROR")
        return
    ADMIN_IDS.discard(uid)
    save_admins(ADMIN_IDS)
    await say(update, context, t(context, "OWNER_REMOVED", uid=uid), sticker_key="OK")


async def listadmins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await owner_list_admins(update, context)


# =========================================================
# АДМИН: СТАТУС УРОВНЕЙ
# =========================================================
async def showlevels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update):
        await say(update, context, t(context, "ACCESS_DENIED"), sticker_key="ERROR")
        return

    lines = [t(context, "STATUS_HEADER")]
    lang = get_lang(context)
    for lvl in LEVELS:
        filled = 0
        for task in TASKS:
            p = get_payload(lvl, task)
            if p and (p.get("video_file_id") or "").strip() and (p.get("description") or "").strip():
                filled += 1
        lines.append(f"• {BTN[f'LEVEL_{lvl}'][lang]} — {filled}/3")

    await say(update, context, "\n".join(lines), reply_markup=kb_admin_levels(context, owner_user=is_owner(update)), sticker_key="ADMIN")


# =========================================================
# ВИДЕО: админ-настройка или видео игрока в канал
# =========================================================
async def on_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.video is None:
        return

    user = update.effective_user
    if not user:
        return

    # если не зарегистрирован — просим зарегистрироваться
    if not is_registered(user.id):
        set_awaiting_registration(context, True)
        await say(update, context, t(context, "NEED_REGISTER_FIRST"), reply_markup=ReplyKeyboardRemove(), sticker_key="ERROR")
        await say(update, context, t(context, "ASK_REGISTER_NAME"), reply_markup=ReplyKeyboardRemove(), sticker_key="WELCOME")
        return

    admin_user = is_admin(update)
    owner_user = is_owner(update)
    mode: Optional[Dict[str, Any]] = context.user_data.get("admin_mode")

    # Если админ в админ-панели и НЕ настраивает задание — не постим в канал случайно
    if admin_user and panel_get(context) == "admin" and not mode:
        await say(update, context, t(context, "ADMIN_VIDEO_WRONG_PANEL"), sticker_key="ERROR")
        return

    # 1) Админ: настройка задания — ждём видео
    if admin_user and mode and mode.get("step") == "wait_video":
        level = int(mode["level"])
        task = int(mode["task"])
        mode["video_file_id"] = update.message.video.file_id
        mode["step"] = "wait_description"
        context.user_data["admin_mode"] = mode

        await say(
            update,
            context,
            t(context, "ADMIN_GOT_VIDEO_SEND_DESC"),
            reply_markup=kb_admin_tasks(context, owner_user=owner_user, level=level),
            sticker_key="ADMIN",
        )
        return

    # 2) Игрок: видео-ответ -> в канал
    lvl = player_level_get(context)
    task = player_task_get(context)
    if lvl is None or task is None:
        await say(
            update,
            context,
            t(context, "NEED_TASK_SELECTED_FOR_VIDEO"),
            reply_markup=kb_player_levels(context, admin_user=admin_user, owner_user=owner_user),
            sticker_key="ERROR",
        )
        return

    registered_name = get_registered_name(user.id)
    username = f"@{user.username}" if user.username else ""

    # ВАЖНО: НЕТ user_id
    caption = (
        f"Pakhtakor Pro — response\n"
        f"Level: {lvl} | Task: {task}\n"
        f"Player: {registered_name} {username}".strip()
    )

    try:
        await context.bot.send_video(
            chat_id=CHANNEL_CHAT_ID,
            video=update.message.video.file_id,
            caption=caption,
        )
    except Exception as e:
        logger.exception("Failed to post to channel: %s", e)
        await say(
            update,
            context,
            t(context, "CANT_POST_TO_CHANNEL"),
            reply_markup=kb_player_tasks(context, admin_user=admin_user, owner_user=owner_user, level=lvl),
            sticker_key="ERROR",
        )
        return

    await say(
        update,
        context,
        t(context, "SENT_TO_CHANNEL_OK"),
        reply_markup=kb_player_tasks(context, admin_user=admin_user, owner_user=owner_user, level=lvl),
        sticker_key="OK",
    )


# =========================================================
# ТЕКСТ / КНОПКИ
# =========================================================
async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.text is None:
        return

    user = update.effective_user
    if not user:
        return

    text_raw = update.message.text.strip()
    text = text_raw.lower()
    admin_user = is_admin(update)
    owner_user = is_owner(update)

    # ---------- выбор языка ----------
    if text in all_btn_texts("LANG_RU"):
        set_lang(context, "ru")
        set_saved_lang(user.id, "ru")

        await say(update, context, t(context, "GREET_AFTER_LANG"), reply_markup=ReplyKeyboardRemove(), sticker_key="WELCOME")

        if not is_registered(user.id):
            set_awaiting_registration(context, True)
            await say(update, context, t(context, "ASK_REGISTER_NAME"), reply_markup=ReplyKeyboardRemove(), sticker_key="WELCOME")
        else:
            set_awaiting_registration(context, False)
            await say(update, context, "📣", reply_markup=channel_button(context), sticker_key="OK")
            await show_current_menu(update, context)
        return

    if text in all_btn_texts("LANG_UZ"):
        set_lang(context, "uz")
        set_saved_lang(user.id, "uz")

        await say(update, context, t(context, "GREET_AFTER_LANG"), reply_markup=ReplyKeyboardRemove(), sticker_key="WELCOME")

        if not is_registered(user.id):
            set_awaiting_registration(context, True)
            await say(update, context, t(context, "ASK_REGISTER_NAME"), reply_markup=ReplyKeyboardRemove(), sticker_key="WELCOME")
        else:
            set_awaiting_registration(context, False)
            await say(update, context, "📣", reply_markup=channel_button(context), sticker_key="OK")
            await show_current_menu(update, context)
        return

    if text in all_btn_texts("LANG_EN"):
        set_lang(context, "en")
        set_saved_lang(user.id, "en")

        await say(update, context, t(context, "GREET_AFTER_LANG"), reply_markup=ReplyKeyboardRemove(), sticker_key="WELCOME")

        if not is_registered(user.id):
            set_awaiting_registration(context, True)
            await say(update, context, t(context, "ASK_REGISTER_NAME"), reply_markup=ReplyKeyboardRemove(), sticker_key="WELCOME")
        else:
            set_awaiting_registration(context, False)
            await say(update, context, "📣", reply_markup=channel_button(context), sticker_key="OK")
            await show_current_menu(update, context)
        return

    # ---------- открыть меню языка ----------
    if is_btn(text_raw, "LANG_MENU"):
        await say(update, context, TXT["CHOOSE_LANG"]["ru"], reply_markup=kb_language(), sticker_key="PANEL")
        return

    # ---------- если ожидаем регистрацию, то любой текст — это попытка имени ----------
    if is_awaiting_registration(context) or not is_registered(user.id):
        if is_btn(text_raw, "CANCEL"):
            set_awaiting_registration(context, False)
            await say(update, context, t(context, "CANCELLED"), sticker_key="OK")
            return

        if is_btn(text_raw, "CHANNEL_BTN"):
            await say(update, context, "📣", reply_markup=channel_button(context), sticker_key="OK")
            return

        candidate = normalize_full_name(text_raw)
        if is_valid_full_name(candidate):
            set_registered_name(user.id, candidate)
            set_awaiting_registration(context, False)
            await say(update, context, t(context, "REGISTER_SAVED", name=candidate), sticker_key="OK")

            await say(update, context, "📣", reply_markup=channel_button(context), sticker_key="OK")

            if is_admin(update):
                await say(update, context, t(context, "CHOOSE_PANEL_ADMIN"), reply_markup=kb_choose_panel(context, owner_user=owner_user), sticker_key="PANEL")
            else:
                await say(update, context, t(context, "PLAYER_START"), reply_markup=kb_player_levels(context, admin_user=False, owner_user=owner_user), sticker_key="PANEL")
            return

        await say(update, context, t(context, "REGISTER_INVALID"), reply_markup=ReplyKeyboardRemove(), sticker_key="ERROR")
        return

    # ---------- КНОПКА 📣 Канал ----------
    if is_btn(text_raw, "CHANNEL_BTN"):
        await say(update, context, "📣", reply_markup=channel_button(context), sticker_key="OK")
        return

    # ---------- HOME ----------
    if is_btn(text_raw, "HOME"):
        if admin_user:
            await say(update, context, t(context, "CHOOSE_PANEL_ADMIN"), reply_markup=kb_choose_panel(context, owner_user=owner_user), sticker_key="PANEL")
        else:
            await say(update, context, t(context, "PLAYER_START"), reply_markup=kb_player_levels(context, admin_user=False, owner_user=owner_user), sticker_key="PANEL")
        return

    # ---------- CANCEL ----------
    if is_btn(text_raw, "CANCEL"):
        if admin_user:
            context.user_data.pop("admin_mode", None)
        if owner_user:
            context.user_data.pop("owner_mode", None)
        await say(update, context, t(context, "CANCELLED"), sticker_key="OK")
        await show_current_menu(update, context)
        return

    # ---------- OWNER FLOW (add/del admins by id) ----------
    owner_mode: Optional[Dict[str, Any]] = context.user_data.get("owner_mode")
    if owner_user and owner_mode:
        step = owner_mode.get("step")
        uid = _extract_user_id_from_text(text_raw)
        if uid is None:
            await say(update, context, t(context, "OWNER_BAD_ID"), sticker_key="ERROR")
            await show_current_menu(update, context)
            return

        if step == "add_admin":
            ADMIN_IDS.add(uid)
            save_admins(ADMIN_IDS)
            context.user_data.pop("owner_mode", None)
            await say(update, context, t(context, "OWNER_ADDED", uid=uid), sticker_key="OK")
            await owner_list_admins(update, context)
            await show_current_menu(update, context)
            return

        if step == "del_admin":
            if uid == OWNER_USER_ID:
                context.user_data.pop("owner_mode", None)
                await say(update, context, t(context, "OWNER_CANNOT_REMOVE_SELF"), sticker_key="ERROR")
                await show_current_menu(update, context)
                return
            ADMIN_IDS.discard(uid)
            save_admins(ADMIN_IDS)
            context.user_data.pop("owner_mode", None)
            await say(update, context, t(context, "OWNER_REMOVED", uid=uid), sticker_key="OK")
            await owner_list_admins(update, context)
            await show_current_menu(update, context)
            return

    # ---------- OWNER buttons ----------
    if owner_user and is_btn(text_raw, "OWNER_LIST_ADMINS"):
        await owner_list_admins(update, context)
        await show_current_menu(update, context)
        return

    if owner_user and is_btn(text_raw, "OWNER_ADD_ADMIN"):
        context.user_data["owner_mode"] = {"step": "add_admin"}
        await say(update, context, t(context, "OWNER_ADD_PROMPT"), sticker_key="PANEL")
        return

    if owner_user and is_btn(text_raw, "OWNER_DEL_ADMIN"):
        context.user_data["owner_mode"] = {"step": "del_admin"}
        await say(update, context, t(context, "OWNER_DEL_PROMPT"), sticker_key="PANEL")
        return

    # ---------- Правила ----------
    if is_btn(text_raw, "RULES"):
        await say(update, context, t(context, "RULES_TEXT"), sticker_key="RULES")
        await show_current_menu(update, context)
        return

    # ---------- Назад к уровням ----------
    if is_btn(text_raw, "BACK_LEVELS"):
        if admin_user and panel_get(context) == "admin":
            admin_level_set(context, None)
            await say(update, context, "OK", reply_markup=kb_admin_levels(context, owner_user=owner_user), sticker_key="OK")
        else:
            player_level_set(context, None)
            player_task_set(context, None)
            await say(update, context, "OK", reply_markup=kb_player_levels(context, admin_user=admin_user, owner_user=owner_user), sticker_key="OK")
        return

    # ---------- Переключение панелей (для админов) ----------
    if admin_user and is_btn(text_raw, "PANEL_ADMIN"):
        panel_set(context, "admin")
        player_level_set(context, None)
        player_task_set(context, None)
        admin_level_set(context, None)
        await say(update, context, t(context, "ADMIN_OPENED"), reply_markup=kb_admin_levels(context, owner_user=owner_user), sticker_key="ADMIN")
        return

    if admin_user and is_btn(text_raw, "PANEL_PLAYER"):
        panel_set(context, "player")
        admin_level_set(context, None)
        player_level_set(context, None)
        player_task_set(context, None)
        await say(update, context, t(context, "PLAYER_OPENED"), reply_markup=kb_player_levels(context, admin_user=True, owner_user=owner_user), sticker_key="PANEL")
        return

    # ---------- Статус уровней (админ) ----------
    if admin_user and panel_get(context) == "admin" and is_btn(text_raw, "STATUS"):
        await showlevels(update, context)
        return

    # ---------- Админ ждёт описание (после видео) ----------
    mode: Optional[Dict[str, Any]] = context.user_data.get("admin_mode")
    if admin_user and mode and mode.get("step") == "wait_description":
        level = int(mode["level"])
        task = int(mode["task"])
        file_id = (mode.get("video_file_id") or "").strip()
        description = text_raw.strip()

        if not file_id:
            context.user_data.pop("admin_mode", None)
            await say(update, context, "Error: missing video id.", reply_markup=kb_admin_levels(context, owner_user=owner_user), sticker_key="ERROR")
            return

        set_payload(level, task, file_id, description)
        context.user_data.pop("admin_mode", None)

        await say(update, context, t(context, "ADMIN_SAVED", lvl=level, task=task), reply_markup=kb_admin_tasks(context, owner_user=owner_user, level=level), sticker_key="ADMIN")
        return

    # =====================================================
    # ОСНОВНАЯ ЛОГИКА ПАНЕЛЕЙ
    # =====================================================
    current_panel = panel_get(context) if admin_user else "player"

    # ---------------------------
    # АДМИН-ПАНЕЛЬ
    # ---------------------------
    if admin_user and current_panel == "admin":
        lvl = parse_level(text_raw)
        if lvl is not None:
            admin_level_set(context, lvl)
            await say(update, context, t(context, "ADMIN_PICK_TASK", lvl=lvl), reply_markup=kb_admin_tasks(context, owner_user=owner_user, level=lvl), sticker_key="ADMIN")
            return

        task = parse_task(text_raw)
        lvl_selected = admin_level_get(context)
        if task is not None:
            if lvl_selected is None:
                await say(update, context, t(context, "NEED_LEVEL_FIRST"), reply_markup=kb_admin_levels(context, owner_user=owner_user), sticker_key="ERROR")
                return

            context.user_data["admin_mode"] = {
                "step": "wait_video",
                "level": lvl_selected,
                "task": task,
                "video_file_id": None,
            }
            await say(update, context, t(context, "ADMIN_SEND_VIDEO", lvl=lvl_selected, task=task), reply_markup=kb_admin_tasks(context, owner_user=owner_user, level=lvl_selected), sticker_key="ADMIN")
            return

        await say(update, context, "OK", reply_markup=kb_admin_levels(context, owner_user=owner_user), sticker_key="ADMIN")
        return

    # ---------------------------
    # ИГРОВАЯ ПАНЕЛЬ
    # ---------------------------
    lvl = parse_level(text_raw)
    if lvl is not None:
        player_level_set(context, lvl)
        player_task_set(context, None)
        await say(update, context, t(context, "LEVEL_CHOSEN", lvl=lvl), reply_markup=kb_player_tasks(context, admin_user=admin_user, owner_user=owner_user, level=lvl), sticker_key="OK")
        return

    task = parse_task(text_raw)
    lvl_selected = player_level_get(context)
    if task is not None:
        if lvl_selected is None:
            await say(update, context, t(context, "NEED_LEVEL_FIRST"), reply_markup=kb_player_levels(context, admin_user=admin_user, owner_user=owner_user), sticker_key="ERROR")
            return

        payload = get_payload(lvl_selected, task)
        if not payload:
            await say(update, context, t(context, "NO_CONTENT", lvl=lvl_selected, task=task), reply_markup=kb_player_tasks(context, admin_user=admin_user, owner_user=owner_user, level=lvl_selected), sticker_key="ERROR")
            return

        video_file_id = (payload.get("video_file_id") or "").strip()
        description = (payload.get("description") or "").strip()
        if not video_file_id:
            await say(update, context, t(context, "NO_CONTENT", lvl=lvl_selected, task=task), reply_markup=kb_player_tasks(context, admin_user=admin_user, owner_user=owner_user, level=lvl_selected), sticker_key="ERROR")
            return

        player_task_set(context, task)

        if update.effective_chat:
            await send_sticker_safe(context, update.effective_chat.id, "OK")

        try:
            await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=video_file_id,
                caption=f"🎬 Pakhtakor Pro — {lvl_selected}/{task}",
            )
        except Exception as e:
            logger.exception("Failed to send task video: %s", e)
            await say(update, context, "❌ Error sending video.", reply_markup=kb_player_tasks(context, admin_user=admin_user, owner_user=owner_user, level=lvl_selected), sticker_key="ERROR")
            return

        if description:
            await say(update, context, f"📝 {description}", sticker_key="OK")

        await say(update, context, t(context, "SEND_RESPONSE"), reply_markup=kb_player_tasks(context, admin_user=admin_user, owner_user=owner_user, level=lvl_selected), sticker_key="OK")
        return

    # fallback
    await show_current_menu(update, context)


# =========================================================
# ЗАПУСК
# =========================================================
def main() -> None:
    if not BOT_TOKEN or "PASTE_YOUR_BOT_TOKEN_HERE" in BOT_TOKEN:
        raise RuntimeError("Вставьте настоящий BOT_TOKEN.")
    if not isinstance(OWNER_USER_ID, int) or OWNER_USER_ID == 123456789:
        raise RuntimeError("Вставьте настоящий OWNER_USER_ID (число).")
    if not CHANNEL_URL.startswith("http"):
        raise RuntimeError("Задайте CHANNEL_URL (https://...).")

    app = Application.builder().token(BOT_TOKEN).build()

    # команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("lang", lang_cmd))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("stickerid", stickerid))
    app.add_handler(CommandHandler("hide", hide))
    app.add_handler(CommandHandler("cancel", cancel_cmd))
    app.add_handler(CommandHandler("showlevels", showlevels))

    # owner backup
    app.add_handler(CommandHandler("addadmin", addadmin))
    app.add_handler(CommandHandler("deladmin", deladmin))
    app.add_handler(CommandHandler("listadmins", listadmins))

    # сообщения
    app.add_handler(MessageHandler(filters.VIDEO, on_video))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    logger.info("Pakhtakor Pro bot started.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

