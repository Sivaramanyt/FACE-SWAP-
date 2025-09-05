from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

# Environment variables with fallback values for testing
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Debug: Check if environment variables are loaded
print(f"API_ID: {API_ID}")
print(f"API_HASH: {'Set' if API_HASH else 'Not Set'}")
print(f"BOT_TOKEN: {'Set' if BOT_TOKEN else 'Not Set'}")

# Convert API_ID to integer
if API_ID:
    API_ID = int(API_ID)

app = Client("face_swap_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📸 Image Swap", callback_data="image_swap")],
        [InlineKeyboardButton("🎥 Video Swap", callback_data="video_swap")],
        [InlineKeyboardButton("💎 Premium", callback_data="premium")]
    ])
    
    welcome_text = f"""🤖 **Face Swap Bot**

✅ **Bot is running successfully!**

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

if __name__ == "__main__":
    print("🚀 Starting Face Swap Bot...")
    print("✅ All systems ready!")
    app.run()
                
