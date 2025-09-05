from pyrogram import filters
from pyrogram.types import Message
from face_swap import FaceSwapper
from database import check_user_limits, update_usage

swapper = FaceSwapper()

@app.on_message(filters.video)
async def handle_video_swap(client, message: Message):
    user_id = message.from_user.id
    
    # Check user limits
    if not check_user_limits(user_id, 'video'):
        await message.reply("⚠️ Daily video swap limit reached! Upgrade to premium.")
        return
    
    await message.reply("🎥 Processing your video swap... This may take a few minutes.")
    
    # Download video
    video_path = await client.download_media(message.video)
    
    if message.reply_to_message and message.reply_to_message.photo:
        face_path = await client.download_media(message.reply_to_message.photo)
        
        # Process video face swap
        result_path = await swapper.process_video_swap(video_path, face_path)
        
        if result_path:
            await client.send_video(message.chat.id, result_path)
            update_usage(user_id, 'video')
        else:
            await message.reply("❌ Video face swap failed.")
    else:
        await message.reply("Please reply to a photo to use as the face for swapping.")
