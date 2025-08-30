import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID") 
    TIMEZONE = os.getenv("TIMEZONE", "Asia/Bishkek")
    REMINDER_TIME = os.getenv("REMINDER_TIME", "20:00")
    # Database URL - поддержка PostgreSQL для Railway
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/bot.db")
    
    # Если Railway PostgreSQL, заменим на правильный драйвер для async
    if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Коды авторизации
    AUTH_CODES = {
        os.getenv("AUTH_CODE_USER1"): "Ислам",
        os.getenv("AUTH_CODE_USER2"): "Куткелди", 
        os.getenv("AUTH_CODE_USER3"): "Пользователь 3"
    }
    
    # Google Credentials путь
    GOOGLE_CREDENTIALS = "./data/credentials.json"

config = Config()