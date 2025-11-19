# telegram/bot.py
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN

# bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
bot = Bot(
    token=BOT_TOKEN,
    # Здесь указываем параметры по умолчанию
    default=DefaultBotProperties(parse_mode="HTML")
)

dp = Dispatcher()
