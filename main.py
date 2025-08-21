import asyncio
import logging
import os
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.filters import Command
from dotenv import load_dotenv
import csv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# Папки
os.makedirs("files", exist_ok=True)
os.makedirs("logs", exist_ok=True)

LOG_FILE = "logs/users.csv"

# Создаём лог-файл если нет
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "username", "first_name", "datetime", "got_pdf"])

# Словарь для антифлуда
user_timers = {}

def log_user(user_id, username, first_name, got_pdf=False):
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([user_id, username, first_name, datetime.now(), got_pdf])

def update_log(user_id):
    rows = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    for row in rows:
        if row and row[0] == str(user_id):
            row[4] = "True"

    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

def main_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="📘 Получить гайд", callback_data="get_guide")
    kb.button(text="🔗 Подписаться на канал", url=f"https://t.me/c/{str(CHANNEL_ID)[4:]}")
    kb.button(text="✅ Проверить подписку", callback_data="check_sub")
    return kb.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    log_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    await message.answer(
        "👋 Привет! Здесь ты можешь получить мой PDF-гайд.
"
        "Чтобы скачать его бесплатно, подпишись на канал и вернись сюда.",
        reply_markup=main_keyboard()
    )

@dp.callback_query(F.data == "check_sub")
async def check_sub(callback: CallbackQuery):
    member = await bot.get_chat_member(CHANNEL_ID, callback.from_user.id)
    if member.status in ("member", "administrator", "creator"):
        await callback.message.answer("✅ Подписка подтверждена! Теперь жми кнопку ниже, чтобы получить гайд.")
    else:
        await callback.message.answer("❌ Ты не подписан. Подпишись на канал и попробуй снова.")

@dp.callback_query(F.data == "get_guide")
async def send_guide(callback: CallbackQuery):
    user_id = callback.from_user.id
    now = datetime.now()

    if user_id in user_timers and now - user_timers[user_id] < timedelta(hours=1):
        await callback.message.answer("⏳ Ты уже получал гайд недавно. Попробуй позже.")
        return

    member = await bot.get_chat_member(CHANNEL_ID, user_id)
    if member.status not in ("member", "administrator", "creator"):
        await callback.message.answer("❌ Сначала подпишись на канал.")
        return

    if not os.path.exists("files/guide.pdf"):
        await callback.message.answer("⚠️ PDF пока недоступен.")
        return

    await callback.message.answer_document(document=open("files/guide.pdf", "rb"))
    await callback.message.answer("Спасибо, что читаешь 🙏 Если понравится — расскажи друзьям ❤️")

    user_timers[user_id] = now
    update_log(user_id)

@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    total, got_pdf = 0, 0
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))[1:]
        total = len(rows)
        got_pdf = sum(1 for r in rows if r and r[4] == "True")

    await message.answer(f"📊 Статистика:
Всего пользователей: {total}
Получили PDF: {got_pdf}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
