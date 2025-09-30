from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
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

async def show_main_menu(update, context):
    keyboard = [
        ['👤 پروفایل من', '📚 منابع درسی'],
        ['📊 گزارش کار روزانه']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🎊 به منوی اصلی خوش آمدید!",
        reply_markup=reply_markup
    )

async def start(update, context):
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
                await show_main_menu(update, context)
            elif status == 'pending':
                await update.message.reply_text("⏳ در انتظار تأیید ادمین...")
            else:
                await update.message.reply_text("❌ حساب شما رد شده است.")
        else:
            cursor.execute(
                "INSERT INTO users (user_id, first_name, status) VALUES (?, ?, 'pending')",
                (user_id, first_name)
            )
            conn.commit()
            
            keyboard = [[InlineKeyboardButton("✅ تأیید کاربر", callback_data=f"approve_{user_id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"👤 کاربر جدید:\n{first_name}",
                reply_markup=reply_markup
            )
            
            await update.message.reply_text("✅ درخواست شما ارسال شد.")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ خطا در پردازش.")

async def handle_admin_callback(update, context):
    query = update.callback_query
    await query.answer()
    
    try:
        data = query.data
        user_id = int(data.split('_')[1])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if data.startswith('approve'):
            cursor.execute("UPDATE users SET status = 'approved' WHERE user_id = ?", (user_id,))
            conn.commit()
            await query.edit_message_text("✅ کاربر تأیید شد.")
            
            await context.bot.send_message(
                chat_id=user_id,
                text="🎉 حساب شما تأیید شد!"
            )
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error: {e}")

async def handle_main_menu(update, context):
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
            await update.message.reply_text(profile_text)
        else:
            await update.message.reply_text("❌ اطلاعات یافت نشد.")
    
    elif text == '📚 منابع درسی':
        await update.message.reply_text("📚 به زودی...")
    
    elif text == '📊 گزارش کار روزانه':
        await update.message.reply_text("📊 به زودی...")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_admin_callback))
    application.add_handler(MessageHandler(filters.TEXT, handle_main_menu))
    
    logger.info("✅ ربات در حال اجراست...")
    
    # اجرای ساده - بدون webhook پیچیده
    application.run_polling()

if __name__ == '__main__':
    main()
