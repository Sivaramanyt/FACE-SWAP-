import logging
from telegram import Update
from telegram.ext import ContextTypes
from face_swap import swap_faces_api

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_image_swap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image swap with debug logging"""
    user_id = update.effective_user.id
    waiting_for = context.user_data.get('waiting_for')
    
    print(f"📸 IMAGE HANDLER DEBUG: Photo received from user {user_id}")
    print(f"🔍 Current waiting_for state: {waiting_for}")
    
    try:
        # Download photo
        photo_file = await update.message.photo[-1].get_file()
        photo_data = await photo_file.download_as_bytearray()
        print(f"📸 Image downloaded: {len(photo_data)} bytes")
        
        # Check what we're waiting for
        if waiting_for == 'image_swap_source':
            # Store source image
            context.user_data['source_image'] = photo_data
            context.user_data['waiting_for'] = 'image_swap_target'
            print("📝 Stored as source image, waiting for target")
            
            await update.message.reply_text(
                "✅ **Source image received!**\n\n📤 **Now send the target image** (face to replace)"
            )
            
        elif waiting_for == 'image_swap_target':
            # Get source image and perform swap
            source_data = context.user_data.get('source_image')
            if not source_data:
                print("❌ ERROR: No source image found in context")
                await update.message.reply_text("❌ Error: Source image not found. Please start over.")
                return
                
            print("🔄 IMAGE HANDLER: About to call face swap API...")
            print(f"📊 Source size: {len(source_data)} bytes")
            print(f"📊 Target size: {len(photo_data)} bytes")
            
            # Call face swap API
            result = await swap_faces_api(source_data, photo_data, 'standard')
            print(f"🎯 IMAGE HANDLER: Result = {'SUCCESS' if result else 'FAILED'}")
            
            if result:
                print("✅ Sending swapped image to user")
                await update.message.reply_photo(
                    photo=result,
                    caption="✅ **Face swap completed!**\n\n💎 Upgrade to Premium for HD quality!"
                )
                logger.info(f"Successfully sent swapped image to user {user_id}")
            else:
                print("❌ Sending error message to user")
                await update.message.reply_text(
                    "❌ **Processing failed!**\n\nPlease try again in a few minutes."
                )
                logger.info(f"Face swap failed for user {user_id}")
            
            # Clear context
            context.user_data.clear()
            print("🧹 Cleared user context")
            
        else:
            print(f"⚠️ Unexpected state: {waiting_for}")
            await update.message.reply_text(
                "📸 **Photo received!**\n\nUse /start to begin face swapping!"
            )
            
    except Exception as e:
        print(f"❌ IMAGE HANDLER EXCEPTION: {str(e)}")
        logger.error(f"Exception in image handler: {e}")
        await update.message.reply_text("❌ **Error processing image!**\n\nPlease try again.")
            
