import os
import asyncio
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv('BOT_TOKEN')
PORT = int(os.getenv('PORT', 8000))

print(f"🚀 Starting Face Swap Bot with token: {BOT_TOKEN[:10]}...")

# Health check
async def health_handler(request):
    return web.Response(text="✅ Face Swap Bot is healthy!")

# Bot handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"📨 START command from {update.effective_user.id}")
    
    keyboard = [
        [InlineKeyboardButton("📸 Image Swap", callback_data="image_swap")],
        [InlineKeyboardButton("🎥 Video Swap", callback_data="video_swap")],
        [InlineKeyboardButton("💎 Premium", callback_data="premium")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""🤖 **Face Swap Bot**

✅ **Bot is running successfully!**
🟢 **Status: Healthy on Koyeb**

**Available Features:**
📸 Image Face Swap (Coming Soon)
🎥 Video Face Swap (Coming Soon)
💎 Premium Features

**User ID:** `{update.effective_user.id}`
**Status:** Active

Choose your swap type:"""
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "image_swap":
        await query.message.reply_text("📸 **Image Face Swap**\n\n🔧 Feature under development!\n✅ Bot is working properly.\n\nSend any photo to test bot response.", parse_mode='Markdown')
    elif query.data == "video_swap":
        await query.message.reply_text("🎥 **Video Face Swap**\n\n🔧 Feature under development!\n✅ Bot is working properly.\n\nSend any video to test bot response.", parse_mode='Markdown')
    elif query.data == "premium":
        await query.message.reply_text("💎 **Premium Features**\n\n🚀 Coming Soon:\n• Unlimited Face Swaps\n• HD Quality Output\n• Priority Processing\n• No Watermarks", parse_mode='Markdown')

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"📷 Photo received from {update.effective_user.id}")
    await update.message.reply_text("📸 **Photo Received!**\n\n✅ Bot is processing images correctly.\n🔧 Face swap feature will be added soon.", parse_mode='Markdown')

async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"🎥 Video received from {update.effective_user.id}")
    await update.message.reply_text("🎥 **Video Received!**\n\n✅ Bot is processing videos correctly.\n🔧 Face swap feature will be added soon.", parse_mode='Markdown')

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 **Hello!**\n\nUse /start to see available options.\n\n✅ Face Swap Bot is working properly!", parse_mode='Markdown')

async def main():
    print("🔧 Starting services...")
    
    # Start health check web server
    health_app = web.Application()
    health_app.router.add_get('/', health_handler)
    health_app.router.add_get('/health', health_handler)
    
    runner = web.AppRunner(health_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"✅ Health server started on port {PORT}")
    
    # Create bot application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    application.add_handler(MessageHandler(filters.VIDEO, video_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    # Start the bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    print("✅ Telegram bot started successfully!")
    print("🤖 Face Swap Bot is fully operational!")
    
    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("🛑 Shutting down...")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
    
