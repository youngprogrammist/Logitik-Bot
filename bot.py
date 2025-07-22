import re
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart, Command
from aiogram.enums import ChatType
from aiogram.client.default import DefaultBotProperties
from aiogram.methods.delete_message import DeleteMessage

API_TOKEN = "7806448787:AAHblqT2XIvT2R_WQatxNxk35OZuzVreFno"

# Kirillga o‘giruvchi funksiya
def to_cyrillic(text):
    mapping = {
        "a": "а", "b": "б", "d": "д", "e": "е", "f": "ф", "g": "г",
        "h": "ҳ", "i": "и", "j": "ж", "k": "к", "l": "л", "m": "м",
        "n": "н", "o": "о", "p": "п", "q": "қ", "r": "р", "s": "с",
        "t": "т", "u": "у", "v": "в", "x": "х", "y": "й", "z": "з",
        "ʼ": "ъ", "'": "ъ", "’": "ъ"
    }
    replacements = [
        ("o‘", "ў"), ("g‘", "ғ"), ("sh", "ш"), ("ch", "ч"), ("ng", "нг"),
        ("ya", "я"), ("yo", "ё"), ("yu", "ю"), ("ye", "е"), ("ts", "ц")
    ]
    text = text.lower()
    for old, new in replacements:
        text = text.replace(old, new)
    return ''.join(mapping.get(c, c) for c in text)

# Kalit so‘zlar
logistics_keywords = [
    "груз", "фура", "дсп", "тент", "комбо", "оплата", "машина", "водитель",
    "йук", "юк", "доставка", "казань", "ташкент", "олмалиқ", "андижон",
    "транспорт", "манзил", "спринтер", "ман", "гафуров", "боғланиш"
]

def is_logistics_related(text):
    text_cyr = to_cyrillic(text.lower())
    return any(kw in text_cyr for kw in logistics_keywords)

# Telefon raqam regex
PHONE_REGEX = re.compile(r"(?:(?:\+|00)998|998)?\s?-?(\d{2})\s?-?(\d{3})\s?-?(\d{2})\s?-?(\d{2})")

def extract_phone_number(text):
    match = PHONE_REGEX.search(text)
    return match.group(0) if match else None

def clean_text(text):
    return PHONE_REGEX.sub('', text)

# E'lon shabloni
def create_template(original_text):
    cleaned = clean_text(original_text.strip())
    template = f"""
______________________

{cleaned}
______________________

Юк билан боғланиш учун 
👉 Номерни кўриш 👈ни босинг!
👇   👇   👇   👇   👇   👇
"""
    return template

# Tugma
def phone_button(phone):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👉 Номерни кўриш 👈", callback_data=f"show:{phone}")]
    ])

# Bot va Dispatcher
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# /start komandasi
@dp.message(CommandStart())
async def start_handler(msg: types.Message):
    await msg.answer("👋 Assalomu alaykum!\n\n📌 Menga yuk e’lonini yuboring, men uni formatlab beraman.\n\n📤 /elon — yangi e'lon yuborish\nℹ️ /help — yordam")

# /help komandasi
@dp.message(Command("help"))
async def help_handler(msg: types.Message):
    await msg.answer("❓ Bot haqida:\n\nMenga yuk tashish bilan bog‘liq e’lonlarni yuboring. Telefon raqam yashirinadi va \"Номерни кўриш\" tugmasi orqali ko‘rinadi.")

# /elon komandasi
@dp.message(Command("elon"))
async def elon_handler(msg: types.Message):
    await msg.answer("📤 E’loningizni yuboring. Men uni avtomatik tarzda formatlab beraman.")

# Matnli xabarlar
@dp.message(F.text)
async def handle_message(msg: types.Message):
    if msg.chat.type == ChatType.PRIVATE:
        await process_ad(msg)

    elif msg.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
        if is_logistics_related(msg.text):
            try:
                await bot(DeleteMessage(chat_id=msg.chat.id, message_id=msg.message_id))
            except:
                pass
            await process_ad(msg)

# E'lonni qayta ishlash
async def process_ad(msg: types.Message):
    phone = extract_phone_number(msg.text)
    if not phone:
        return
    text_cyr = to_cyrillic(msg.text)
    formatted = create_template(text_cyr)
    kb = phone_button(phone)
    await msg.answer(formatted, reply_markup=kb)

# Callback tugma
@dp.callback_query(F.data.startswith("show:"))
async def show_number(callback: types.CallbackQuery):
    phone = callback.data.split(":", 1)[1]
    await callback.message.answer(f"📞 {phone}")
    await callback.answer()

# Ishga tushirish
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
