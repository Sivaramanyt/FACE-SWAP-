from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from face_swap import process_image_swap, process_video_swap

API_ID = 'YOUR_API_ID'
API_HASH = 'YOUR_API_HASH'  
BOT_TOKEN = 'YOUR_BOT_TOKEN'

app = Client("face_swap_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📸 Image Swap", callback_data="image_swap")],
        [InlineKeyboardButton("🎥 Video Swap", callback_data="video_swap")],
        [InlineKeyboardButton("💎 Premium", callback_data="premium")]
    ])
    await message.reply("🤖 **Face Swap Bot**\n\nChoose your swap type:", reply_markup=keyboard)

@app.on_callback_query(filters.regex("image_swap|video_swap|premium"))
async def button_click(client, callback_query):
    data = callback_query.data
    if data == "image_swap":
        await callback_query.message.reply("Please send two images for face swap.")
    elif data == "video_swap":
        await callback_query.message.reply("Please send a video and a face image for video face swap.")
    elif data == "premium":
        await callback_query.message.reply("Premium features coming soon!")

app.run()
