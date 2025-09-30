from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import sqlite3
import os
import logging
from config import BOT_TOKEN, ADMIN_ID, DATABASE_NAME

# تنظیمات لاگ
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
        ['📅 برنامه ریزی', '📊 گزارش کار روزانه'],
        ['🎯 ثبت نتایج آزمون', '📞 ارتباط با مشاور']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🎊 به منوی اصلی خوش آمدید!\n\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
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
                await update.message.reply_text("⏳ حساب شما در انتظار تأیید ادمین است.")
            else:
                await update.message.reply_text("❌ حساب شما رد شده است.")
        else:
            cursor.execute(
                "INSERT INTO users (user_id, first_name, status) VALUES (?, ?, 'pending')",
                (user_id, first_name)
            )
            conn.commit()
            
            keyboard = [
                [InlineKeyboardButton("✅ تأیید کاربر", callback_data=f"approve_{user_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"👤 کاربر جدید:\n{first_name}\nID: {user_id}",
                reply_markup=reply_markup
            )
            
            await update.message.reply_text("✅ درخواست شما برای تأیید ارسال شد.")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error in start: {e}")
        await update.message.reply_text("❌ خطا در پردازش درخواست.")

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
            await query.edit_message_text(f"✅ کاربر تأیید شد.")
            
            await context.bot.send_message(
                chat_id=user_id,
                text="🎉 حساب شما تأیید شد! از /menu برای منوی اصلی استفاده کنید."
            )
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error in admin callback: {e}")

async def handle_main_menu(update, context):
    text = update.message.text
    
    try:
        if text == '👤 پروفایل من':
            user_id = update.effective_user.id
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                profile_text = f"""
👤 پروفایل شما:

📝 نام: {user['first_name']}
🎓 پایه: {user['grade'] or 'ثبت نشده'}
📍 استان: {user['province'] or 'ثبت نشده'}
📞 تلفن: {user['phone'] or 'ثبت نشده'}
                """
                await update.message.reply_text(profile_text)
            else:
                await update.message.reply_text("❌ اطلاعات پروفایل یافت نشد.")
        
        elif text == '📚 منابع درسی':
            await update.message.reply_text("📚 بخش منابع درسی به زودی فعال می‌شود...")
        
        elif text == '📅 برنامه ریزی':
            await update.message.reply_text("📅 بخش برنامه ریزی به زودی فعال می‌شود...")
        
        elif text == '📊 گزارش کار روزانه':
            await update.message.reply_text("📊 بخش گزارش کار روزانه به زودی فعال می‌شود...")
        
        elif text == '🎯 ثبت نتایج آزمون':
            await update.message.reply_text("🎯 بخش ثبت نتایج آزمون به زودی فعال می‌شود...")
        
        elif text == '📞 ارتباط با مشاور':
            await update.message.reply_text("📞 برای ارتباط با مشاور:\n@ali0haghighi")
    
    except Exception as e:
        logger.error(f"Error in main menu: {e}")
        await update.message.reply_text("❌ خطا در پردازش درخواست.")

async def reset_users(update, context):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id != ?", (ADMIN_ID,))
        conn.commit()
        conn.close()
        await update.message.reply_text("✅ تمام کاربران ریست شدند.")
    except Exception as e:
        logger.error(f"Error in reset: {e}")

def main():
    # ساخت اپلیکیشن
    application = Application.builder().token(BOT_TOKEN).build()
    
    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset_users))
    application.add_handler(CommandHandler("menu", show_main_menu))
    application.add_handler(CallbackQueryHandler(handle_admin_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu))
    
    logger.info("✅ ربات در حال اجراست...")
    
    # بررسی اگر روی سرور هستیم
    if "RENDER" in os.environ:
        # روی سرور - از Webhook استفاده می‌کنیم
        port = int(os.environ.get("PORT", 10000))
        webhook_url = f"https://your-bot-name.onrender.com/{BOT_TOKEN}"
        
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=BOT_TOKEN,
            webhook_url=webhook_url
        )
    else:
        # روی سیستم لوکال
        application.run_polling(
            poll_interval=3.0,
            drop_pending_updates=True
        )

if __name__ == '__main__':
    main()
