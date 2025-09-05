import os
import asyncio
import logging
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Enable logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🚀 Face Swap Bot initializing...")

# Get environment variables
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
PORT = int(os.getenv('PORT', 8000))

print(f"✅ Credentials loaded - API_ID: {API_ID}, PORT: {PORT}")

# Initialize Pyrogram client with specific parameters for Koyeb
app = Client(
    "face_swap_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir=".",
    sleep_threshold=180  # Important for Koyeb stability
)

# Health check endpoints
async def health_check(request):
    return web.Response(text="✅ Face Swap Bot is healthy!", status=200)

async def root_handler(request):
    return web.Response(text="🤖 Face Swap Bot is running!", status=200)

# Bot handlers
@app.on_message(filters.command("start"))
async def start_command(client, message):
    print(f"📨 Received /start from user {message.from_user.id}")
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📸 Image Swap", callback_data="image_swap")],
        [InlineKeyboardButton("🎥 Video Swap", callback_data="video_swap")],
        [InlineKeyboardButton("💎 Premium", callback_data="premium")]
    ])
    
    welcome_text = f"""🤖 **Face Swap Bot**

✅ **Bot is running successfully!**
🟢 **Status: Healthy on Koyeb**

**Available Features:**
📸 Image Face Swap (Coming Soon)
🎥 Video Face Swap (Coming Soon)
💎 Premium Features

**User ID:** `{message.from_user.id}`
**Status:** Active

Choose your swap type:"""
    
    try:
        await message.reply(welcome_text, reply_markup=keyboard)
        print("✅ Start message sent successfully")
    except Exception as e:
        print(f"❌ Error sending start message: {e}")

@app.on_callback_query()
async def handle_callbacks(client, callback_query):
    print(f"🔘 Button pressed: {callback_query.data}")
    
    data = callback_query.data
    try:
        if data == "image_swap":
            await callback_query.message.reply("📸 **Image Face Swap**\n\n🔧 Feature under development!\n✅ Bot is working properly.\n\nSend any photo to test bot response.")
        elif data == "video_swap":
            await callback_query.message.reply("🎥 **Video Face Swap**\n\n🔧 Feature under development!\n✅ Bot is working properly.\n\nSend any video to test bot response.")
        elif data == "premium":
            await callback_query.message.reply("💎 **Premium Features**\n\n🚀 Coming Soon:\n• Unlimited Face Swaps\n• HD Quality Output\n• Priority Processing\n• No Watermarks")
        
        await callback_query.answer()
        print("✅ Callback handled successfully")
    except Exception as e:
        print(f"❌ Error handling callback: {e}")

@app.on_message(filters.photo)
async def handle_photo(client, message):
    print(f"📷 Photo received from user {message.from_user.id}")
    try:
        await message.reply("📸 **Photo Received!**\n\n✅ Bot is processing images correctly.\n🔧 Face swap feature will be added soon.")
        print("✅ Photo response sent")
    except Exception as e:
        print(f"❌ Error handling photo: {e}")

@app.on_message(filters.video)
async def handle_video(client, message):
    print(f"🎥 Video received from user {message.from_user.id}")
    try:
        await message.reply("🎥 **Video Received!**\n\n✅ Bot is processing videos correctly.\n🔧 Face swap feature will be added soon.")
        print("✅ Video response sent")
    except Exception as e:
        print(f"❌ Error handling video: {e}")

@app.on_message(filters.text & ~filters.command(["start"]))
async def handle_text(client, message):
    try:
        await message.reply("👋 **Hello!**\n\nUse /start to see available options.\n\n✅ Face Swap Bot is working properly!")
    except Exception as e:
        print(f"❌ Error handling text: {e}")

# Main function
async def main():
    print("🔧 Starting Face Swap Bot services...")
    
    # Start health check web server
    health_app = web.Application()
    health_app.router.add_get('/', root_handler)
    health_app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(health_app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"✅ Health server started on port {PORT}")
    
    # Start Telegram bot
    try:
        await app.start()
        print("✅ Telegram bot started successfully!")
        print("🤖 Face Swap Bot is fully operational!")
        
        # Get bot info
        me = await app.get_me()
        print(f"📱 Bot username: @{me.username}")
        
    except Exception as e:
        print(f"❌ Error starting Telegram bot: {e}")
        return
    
    # Keep running
    print("🔄 Bot is running... Press Ctrl+C to stop")
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("🛑 Shutting down...")
    finally:
        await app.stop()
        await runner.cleanup()

if __name__ == "__main__":
    print("⚡ Initializing Face Swap Bot...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 Face Swap Bot shutdown complete")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
    
