import os
import logging
import sqlite3
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

# تنظیمات
BOT_TOKEN = os.getenv("BOT_TOKEN", "8309891212:AAGwXLYA8exQRmmANKoUYeuk3M0-de71FWo")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6007509801"))
DATABASE_NAME = "education_bot.db"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_db_connection():
    return sqlite3.connect(DATABASE_NAME)

def start(update, context):
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT status FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
        if user:
            if user[0] == 'approved':
                update.message.reply_text("✅ شما تأیید شده‌اید!")
            else:
                update.message.reply_text("⏳ در انتظار تأیید...")
        else:
            cursor.execute(
                "INSERT INTO users (user_id, first_name, status) VALUES (?, ?, 'pending')",
                (user_id, first_name)
            )
            conn.commit()
            
            # ارسال به ادمین
            keyboard = [[InlineKeyboardButton("✅ تأیید کاربر", callback_data=f"approve_{user_id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"👤 کاربر جدید:\n{first_name}",
                reply_markup=reply_markup
            )
            
            update.message.reply_text("✅ درخواست شما ارسال شد.")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"خطا: {e}")
        update.message.reply_text("❌ خطا در پردازش.")

def button_handler(update, context):
    query = update.callback_query
    query.answer()
    
    try:
        data = query.data
        user_id = int(data.split('_')[1])
        
        if data.startswith('approve'):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET status = 'approved' WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            
            query.edit_message_text("✅ کاربر تأیید شد.")
            context.bot.send_message(chat_id=user_id, text="🎉 حساب شما تأیید شد!")
            
    except Exception as e:
        logger.error(f"خطا: {e}")

def main():
    # ساخت آپدیتور
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    # اضافه کردن هندلرها
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("✅ ربات شروع به کار کرد...")
    
    # اجرای ربات
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
