import logging
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# تنظیمات ساده
BOT_TOKEN = "8309891212:AAGwXLYA8exQRmmANKoUYeuk3M0-de71FWo"
ADMIN_ID = 6007509801

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update, context):
    user = update.message.from_user
    logger.info(f"User {user.first_name} started")
    
    update.message.reply_text(
        f"سلام {user.first_name}! 👋\n"
        f"ربات مشاوره تحصیلی فعال است!"
    )

def main():
    logger.info("Starting bot...")
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    
    logger.info("Bot started successfully!")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
