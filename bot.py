import os
import logging
import sqlite3
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

# تنظیمات
BOT_TOKEN = "8309891212:AAGwXLYA8exQRmmANKoUYeuk3M0-de71FWo"
ADMIN_ID = 6007509801
DATABASE_NAME = "education_bot.db"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    return sqlite3.connect(DATABASE_NAME)

def start(update, context):
    user = update.message.from_user
    logger.info(f"User {user.first_name} started the bot")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT status FROM users WHERE user_id = ?", (user.id,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        status = existing_user[0]
        if status == 'approved':
            update.message.reply_text("✅ شما قبلاً تأیید شده‌اید!")
        else:
            update.message.reply_text("⏳ در انتظار تأیید ادمین...")
    else:
        cursor.execute(
            "INSERT INTO users (user_id, first_name, status) VALUES (?, ?, 'pending')",
            (user.id, user.first_name)
        )
        conn.commit()
        
        # دکمه تأیید برای ادمین
        keyboard = [[InlineKeyboardButton("✅ تأیید کاربر", callback_data=f"approve_{user.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"👤 کاربر جدید:\n{user.first_name}\nID: {user.id}",
            reply_markup=reply_markup
        )
        
        update.message.reply_text("✅ درخواست شما برای تأیید ارسال شد.")
    
    conn.close()

def button_handler(update, context):
    query = update.callback_query
    query.answer()
    
    data = query.data
    user_id = int(data.split('_')[1])
    
    if data.startswith('approve'):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET status = 'approved' WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        
        query.edit_message_text("✅ کاربر تأیید شد.")
        context.bot.send_message(chat_id=user_id, text="🎉 حساب شما تأیید شد! خوش آمدید.")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("✅ ربات شروع به کار کرد...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
