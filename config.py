import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8309891212:AAGwXLYA8exQRmmANKoUYeuk3M0-de71FWo")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6007509801"))
DATABASE_NAME = os.getenv("DATABASE_NAME", "education_bot.db")
