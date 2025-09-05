from pyrogram import filters
from pyrogram.types import Message
from face_swap import FaceSwapper
from database import check_user_limits, update_usage

swapper = FaceSwapper()

@app.on_message(filters.photo)
async def handle_image_swap(client, message: Message):
    user_id = message.from_user.id
    
    # Check user limits
    if not check_user_limits(user_id, 'image'):
        await message.reply("⚠️ Daily limit reached! Upgrade to premium for unlimited swaps.")
        return
    
    await message.reply("📸 Processing your image swap... Please wait.")
    
    # Download and process images
    image_path = await client.download_media(message.photo)
    
    if message.reply_to_message and message.reply_to_message.photo:
        target_path = await client.download_media(message.reply_to_message.photo)
        
        # Process face swap
        result = await swapper.process_image_swap(image_path, target_path)
        
        if result is not None:
            cv2.imwrite('swapped_image.jpg', result)
            await client.send_photo(message.chat.id, 'swapped_image.jpg')
            update_usage(user_id, 'image')
        else:
            await message.reply("❌ Face swap failed. Make sure both images contain clear faces.")
    else:
        await message.reply("Please reply to another photo to swap faces.")
