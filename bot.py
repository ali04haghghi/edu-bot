from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import sqlite3
import os
import logging
from config import BOT_TOKEN, ADMIN_ID, DATABASE_NAME

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def show_main_menu(bot, update):
    keyboard = [
        ['👤 پروفایل من', '📚 منابع درسی'],
        ['📅 برنامه ریزی', '📊 گزارش کار روزانه'],
        ['🎯 ثبت نتایج آزمون', '📞 ارتباط با مشاور']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(
        "🎊 به منوی اصلی خوش آمدید!",
        reply_markup=reply_markup
    )

def start(bot, update):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT status FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
        if user:
            status = user['status']
            if status == 'approved':
                show_main_menu(bot, update)
            elif status == 'pending':
                update.message.reply_text("⏳ در انتظار تأیید ادمین...")
            else:
                update.message.reply_text("❌ حساب شما رد شده است.")
        else:
            cursor.execute(
                "INSERT INTO users (user_id, first_name, status) VALUES (?, ?, 'pending')",
                (user_id, first_name)
            )
            conn.commit()
            
            keyboard = [[InlineKeyboardButton("✅ تأیید کاربر", callback_data=f"approve_{user_id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            bot.send_message(
                chat_id=ADMIN_ID,
                text=f"👤 کاربر جدید:\n{first_name}",
                reply_markup=reply_markup
            )
            
            update.message.reply_text("✅ درخواست شما ارسال شد.")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        update.message.reply_text("❌ خطا در پردازش.")

def handle_admin_callback(bot, update):
    query = update.callback_query
    query.answer()
    
    try:
        data = query.data
        user_id = int(data.split('_')[1])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if data.startswith('approve'):
            cursor.execute("UPDATE users SET status = 'approved' WHERE user_id = ?", (user_id,))
            conn.commit()
            query.edit_message_text("✅ کاربر تأیید شد.")
            
            bot.send_message(
                chat_id=user_id,
                text="🎉 حساب شما تأیید شد! از /menu استفاده کنید."
            )
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error: {e}")

def handle_main_menu(bot, update):
    text = update.message.text
    
    if text == '👤 پروفایل من':
        user_id = update.effective_user.id
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            profile_text = f"👤 نام: {user['first_name']}"
            update.message.reply_text(profile_text)
        else:
            update.message.reply_text("❌ اطلاعات یافت نشد.")
    
    elif text == '📚 منابع درسی':
        update.message.reply_text("📚 به زودی...")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(handle_admin_callback))
    dp.add_handler(MessageHandler(Filters.text, handle_main_menu))
    
    if "RENDER" in os.environ:
        port = int(os.environ.get("PORT", 10000))
        updater.start_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=BOT_TOKEN
        )
        updater.bot.set_webhook(f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{BOT_TOKEN}")
    else:
        updater.start_polling()
    
    updater.idle()

if __name__ == '__main__':
    main()
