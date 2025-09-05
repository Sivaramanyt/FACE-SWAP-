from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import asyncio
from aiohttp import web
import threading

# Your bot credentials
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

if API_ID:
    API_ID = int(API_ID)

app = Client("face_swap_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Health check server for Koyeb
async def health_check(request):
    return web.Response(text="✅ Face Swap Bot is healthy and running!", status=200)

async def start_health_server():
    health_app = web.Application()
    health_app.router.add_get('/', health_check)
    health_app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(health_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()
    print("✅ Health check server started on port 8000")

# Your existing bot handlers (keep exactly the same)
@app.on_message(filters.command("start"))
async def start_command(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📸 Image Swap", callback_data="image_swap")],
        [InlineKeyboardButton("🎥 Video Swap", callback_data="video_swap")],
        [InlineKeyboardButton("💎 Premium", callback_data="premium")]
    ])
    
    welcome_text = f"""🤖 **Face Swap Bot**

✅ **Bot is running successfully!**
🟢 **Status: Healthy**

**Available Features:**
📸 Image Face Swap (Coming Soon)
🎥 Video Face Swap (Coming Soon)
💎 Premium Features

**User ID:** `{message.from_user.id}`
**Status:** Active

Choose your swap type:"""
    
    await message.reply(welcome_text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("image_swap|video_swap|premium"))
async def button_click(client, callback_query):
    data = callback_query.data
    if data == "image_swap":
        await callback_query.message.reply("📸 **Image Face Swap**\n\n🔧 Feature under development!\n✅ Bot is working properly.\n\nSend any photo to test bot response.")
    elif data == "video_swap":
        await callback_query.message.reply("🎥 **Video Face Swap**\n\n🔧 Feature under development!\n✅ Bot is working properly.\n\nSend any video to test bot response.")
    elif data == "premium":
        await callback_query.message.reply("💎 **Premium Features**\n\n🚀 Coming Soon:\n• Unlimited Face Swaps\n• HD Quality Output\n• Priority Processing\n• No Watermarks")

@app.on_message(filters.photo)
async def handle_image(client, message):
    await message.reply("📸 **Photo Received!**\n\n✅ Bot is processing images correctly.\n🔧 Face swap feature will be added soon.\n\n**File Info:**\n• Type: Photo\n• Size: Available\n• User: " + str(message.from_user.first_name))

@app.on_message(filters.video)
async def handle_video(client, message):
    await message.reply("🎥 **Video Received!**\n\n✅ Bot is processing videos correctly.\n🔧 Face swap feature will be added soon.\n\n**File Info:**\n• Type: Video\n• Duration: Available\n• User: " + str(message.from_user.first_name))

@app.on_message(filters.text & ~filters.command(["start"]))
async def handle_text(client, message):
    await message.reply("👋 **Hello!**\n\nUse /start to see available options.\n\n✅ Face Swap Bot is working properly!")

# Start both health server and bot
async def main():
    # Start health check server
    await start_health_server()
    
    # Start the bot
    print("🚀 Starting Face Swap Bot...")
    print("✅ All systems ready!")
    await app.start()
    
    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
    
