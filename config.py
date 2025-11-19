#config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

# Корневой путь проекта
BASE_DIR = Path(__file__).resolve().parent

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Пути к файлам хранения
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

USERS_FILE = DATA_DIR / "users.db"
SCHEDULE_FILE = DATA_DIR / "schedule"
ATTENDANCE_FILE = DATA_DIR / "attendance"
SUBSCRIPTIONS_FILE = DATA_DIR / "subscriptions"

# Настройки логов (если понадобятся)
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Default settings (на будущее)
DEFAULT_LANGUAGE = "ru"
