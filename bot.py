from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os

# Remove face_swap import for now
# from face_swap import process_image_swap, process_video_swap

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

app = Client("face_swap_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📸 Image Swap", callback_data="image_swap")],
        [InlineKeyboardButton("🎥 Video Swap", callback_data="video_swap")],
        [InlineKeyboardButton("💎 Premium", callback_data="premium")]
    ])
    await message.reply("🤖 **Face Swap Bot**\n\n✅ Bot is running successfully!\n\nChoose your swap type:", reply_markup=keyboard)

@app.on_callback_query(filters.regex("image_swap|video_swap|premium"))
async def button_click(client, callback_query):
    data = callback_query.data
    if data == "image_swap":
        await callback_query.message.reply("📸 Image swap feature coming soon!\n\nBot is working properly.")
    elif data == "video_swap":
        await callback_query.message.reply("🎥 Video swap feature coming soon!\n\nBot is working properly.")
    elif data == "premium":
        await callback_query.message.reply("💎 Premium features coming soon!")

@app.on_message(filters.photo)
async def handle_image(client, message):
    await message.reply("📸 Photo received! Face swap processing will be added soon.")

@app.on_message(filters.video)
async def handle_video(client, message):
    await message.reply("🎥 Video received! Face swap processing will be added soon.")

print("Starting Face Swap Bot...")
app.run()
        
