import asyncio
import json
import requests
import base64
from datetime import datetime, date, timedelta
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import logging

# Import configuration
from config import *

# Setup logging
logging.basicConfig(level=getattr(logging, LOGGING_CONFIG['level']), format=LOGGING_CONFIG['format'])
logger = logging.getLogger(__name__)

print(f"🚀 Starting Face Swap Bot on port {PORT}...")

# User database functions
def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users_data):
    with open(USERS_FILE, 'w') as f:
        json.dump(users_data, f, indent=2)

def get_user_data(user_id):
    users = load_users()
    today = str(date.today())
    
    if str(user_id) not in users:
        users[str(user_id)] = {
            'premium': False,
            'premium_expiry': None,
            'daily_usage': {
                'date': today,
                'image_swaps': 0,
                'video_swaps': 0
            },
            'total_swaps': 0,
            'join_date': today,
            'last_active': today
        }
        save_users(users)
        logger.info(f"New user registered: {user_id}")
    
    user = users[str(user_id)]
    
    # Check premium expiry
    if user.get('premium') and user.get('premium_expiry'):
        expiry_date = datetime.strptime(user['premium_expiry'], '%Y-%m-%d').date()
        if date.today() > expiry_date:
            user['premium'] = False
            user['premium_expiry'] = None
            logger.info(f"Premium expired for user {user_id}")
    
    # Reset daily usage if new day
    if user.get('daily_usage', {}).get('date') != today:
        user['daily_usage'] = {
            'date': today,
            'image_swaps': 0,
            'video_swaps': 0
        }
    
    user['last_active'] = today
    users[str(user_id)] = user
    save_users(users)
    
    return user

def update_usage(user_id, swap_type):
    users = load_users()
    user = users.get(str(user_id), {})
    
    if swap_type == 'image':
        user['daily_usage']['image_swaps'] += 1
    elif swap_type == 'video':
        user['daily_usage']['video_swaps'] += 1
    
    user['total_swaps'] = user.get('total_swaps', 0) + 1
    users[str(user_id)] = user
    save_users(users)
    logger.info(f"Usage updated for user {user_id}: {swap_type}")

def check_limits(user_data, swap_type):
    if user_data.get('premium', False):
        limits = PREMIUM_LIMITS
        return True, "unlimited"
    else:
        limits = FREE_LIMITS
    
    usage = user_data.get('daily_usage', {})
    if swap_type == 'image':
        used = usage.get('image_swaps', 0)
        limit = limits['daily_image_swaps']
        return used < limit, f"{used}/{limit}"
    elif swap_type == 'video':
        used = usage.get('video_swaps', 0)
        limit = limits['daily_video_swaps']
        return used < limit, f"{used}/{limit}"
    
    return False, "0/0"

def activate_premium(user_id, plan):
    users = load_users()
    user = users.get(str(user_id), {})
    
    duration_days = PRICING[plan]['duration_days']
    expiry_date = date.today() + timedelta(days=duration_days)
    
    user['premium'] = True
    user['premium_expiry'] = expiry_date.strftime('%Y-%m-%d')
    user['premium_plan'] = plan
    user['premium_activated'] = str(date.today())
    
    users[str(user_id)] = user
    save_users(users)
    logger.info(f"Premium activated for user {user_id}: {plan} plan")

# Face swap API functions
async def swap_faces_api(source_image_data, target_image_data, quality='standard'):
    """Face swap using RapidAPI"""
    try:
        # Convert images to base64
        source_b64 = base64.b64encode(source_image_data).decode()
        target_b64 = base64.b64encode(target_image_data).decode()
        
        url = FACE_SWAP_API_CONFIG['base_url'] + FACE_SWAP_API_CONFIG['endpoints']['image_swap']
        
        payload = {
            "source_image": source_b64,
            "target_image": target_b64,
            "face_enhance": quality == 'hd'
        }
        
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            **FACE_SWAP_API_CONFIG['headers']
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=FACE_SWAP_API_CONFIG['timeout'])
        
        if response.status_code == 200:
            result = response.json()
            return base64.b64decode(result.get('result_image', ''))
        else:
            logger.error(f"Face swap API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Face swap API exception: {e}")
        return None

async def swap_video_api(video_data, face_image_data, quality='standard'):
    """Video face swap using RapidAPI"""
    try:
        video_b64 = base64.b64encode(video_data).decode()
        face_b64 = base64.b64encode(face_image_data).decode()
        
        url = FACE_SWAP_API_CONFIG['base_url'] + FACE_SWAP_API_CONFIG['endpoints']['video_swap']
        
        payload = {
            "video": video_b64,
            "face_image": face_b64,
            "quality": quality
        }
        
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            **FACE_SWAP_API_CONFIG['headers']
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=300)  # Longer timeout for videos
        
        if response.status_code == 200:
            result = response.json()
            return base64.b64decode(result.get('result_video', ''))
        else:
            logger.error(f"Video swap API error: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Video swap API exception: {e}")
        return None

# Health check
async def health_handler(request):
    return web.Response(text="✅ Face Swap Bot is healthy!")

# Bot handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    
    logger.info(f"START command from user {user_id}")
    
    # Check usage status
    image_allowed, image_status = check_limits(user_data, 'image')
    video_allowed, video_status = check_limits(user_data, 'video')
    
    keyboard = [
        [InlineKeyboardButton("📸 Image Swap", callback_data="image_swap")],
        [InlineKeyboardButton("🎥 Video Swap", callback_data="video_swap")],
        [InlineKeyboardButton("💎 Premium", callback_data="premium")],
        [InlineKeyboardButton("📊 My Usage", callback_data="usage")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    premium_status = "🟢 Premium" if user_data.get('premium') else "🆓 Free"
    
    welcome_text = MESSAGES['welcome'].format(
        premium_status=premium_status,
        image_status=image_status,
        video_status=video_status,
        total_swaps=user_data.get('total_swaps', 0),
        user_id=user_id
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user_data = get_user_data(user_id)
    
    await query.answer()
    
    if query.data == "image_swap":
        can_swap, status = check_limits(user_data, 'image')
        if can_swap:
            context.user_data['waiting_for'] = 'image_swap_source'
            await query.message.reply_text(MESSAGES['image_swap_start'], parse_mode='Markdown')
        else:
            await query.message.reply_text(
                MESSAGES['limit_reached'].format(swap_type='Image', status=status),
                parse_mode='Markdown'
            )
    
    elif query.data == "video_swap":
        can_swap, status = check_limits(user_data, 'video')
        if can_swap:
            context.user_data['waiting_for'] = 'video_swap_video'
            await query.message.reply_text(MESSAGES['video_swap_start'], parse_mode='Markdown')
        else:
            await query.message.reply_text(
                MESSAGES['limit_reached'].format(swap_type='Video', status=status),
                parse_mode='Markdown'
            )
    
    elif query.data == "premium":
        keyboard = [
            [InlineKeyboardButton(f"💳 Weekly {PRICING['weekly']['currency']}{PRICING['weekly']['price']}", callback_data="buy_weekly")],
            [InlineKeyboardButton(f"💳 Monthly {PRICING['monthly']['currency']}{PRICING['monthly']['price']}", callback_data="buy_monthly")],
            [InlineKeyboardButton(f"💳 Yearly {PRICING['yearly']['currency']}{PRICING['yearly']['price']}", callback_data="buy_yearly")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(MESSAGES['premium_features'], reply_markup=reply_markup, parse_mode='Markdown')
    
    elif query.data == "usage":
        image_allowed, image_status = check_limits(user_data, 'image')
        video_allowed, video_status = check_limits(user_data, 'video')
        
        premium_info = ""
        if user_data.get('premium'):
            expiry = user_data.get('premium_expiry', 'N/A')
            premium_info = f"**Premium Plan:** {user_data.get('premium_plan', 'Unknown').title()}\n**Expires:** {expiry}\n\n"
        
        usage_text = f"""📊 **Your Usage Statistics**

**Account Type:** {'🟢 Premium' if user_data.get('premium') else '🆓 Free'}

{premium_info}**Today's Usage:**
📸 Image Swaps: {image_status}
🎥 Video Swaps: {video_status}

**All Time:**
📈 Total Swaps: {user_data.get('total_swaps', 0)}
📅 Member Since: {user_data.get('join_date', 'Unknown')}

💡 Upgrade to Premium for unlimited swaps!"""
        
        await query.message.reply_text(usage_text, parse_mode='Markdown')
    
    elif query.data.startswith("buy_"):
        plan = query.data.replace("buy_", "")
        plan_config = PRICING[plan]
        
        payment_text = MESSAGES['payment_instructions'].format(
            plan=plan.title(),
            price=f"{plan_config['currency']}{plan_config['price']}",
            gpay_number=PAYMENT_CONFIG['gpay_number'],
            phonepe_number=PAYMENT_CONFIG['phonepe_number'],
            upi_id=PAYMENT_CONFIG['upi_id'],
            support_username=PAYMENT_CONFIG['support_username']
        )
        
        await query.message.reply_text(payment_text, parse_mode='Markdown')
    
    elif query.data == "back_main":
        await start_command(update, context)

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    waiting_for = context.user_data.get('waiting_for')
    
    logger.info(f"Photo received from user {user_id}, waiting_for: {waiting_for}")
    
    # Check file size
    photo_size = update.message.photo[-1].file_size
    max_size = PREMIUM_LIMITS['max_file_size'] if user_data.get('premium') else FREE_LIMITS['max_file_size']
    
    if photo_size > max_size:
        await update.message.reply_text(
            ERROR_MESSAGES['file_too_large'].format(max_size=max_size // (1024*1024)),
            parse_mode='Markdown'
        )
        return
    
    if waiting_for == 'image_swap_source':
        # Store source image
        photo_file = await update.message.photo[-1].get_file()
        photo_data = await photo_file.download_as_bytearray()
        context.user_data['source_image'] = photo_data
        context.user_data['waiting_for'] = 'image_swap_target'
        
        await update.message.reply_text("""✅ **Source image received!**

📤 **Now send the target image** (the face you want to replace)

🔄 Processing will start automatically after receiving both images...""", parse_mode='Markdown')
    
    elif waiting_for == 'image_swap_target':
        # Process face swap
        quality = 'hd' if user_data.get('premium') else 'standard'
        processing_time = "30-60 seconds" if quality == 'standard' else "60-120 seconds"
        
        await update.message.reply_text(
            MESSAGES['processing'].format(swap_type="face swap", time=processing_time),
            parse_mode='Markdown'
        )
        
        photo_file = await update.message.photo[-1].get_file()
        target_data = await photo_file.download_as_bytearray()
        source_data = context.user_data.get('source_image')
        
        # Perform face swap
        result = await swap_faces_api(source_data, target_data, quality)
        
        if result:
            # Send result
            await update.message.reply_photo(
                photo=result,
                caption="✅ **Face swap completed!**\n\n💎 Upgrade to Premium for HD quality and no watermarks!"
            )
            update_usage(user_id, 'image')
            logger.info(f"Successful image swap for user {user_id}")
        else:
            await update.message.reply_text(ERROR_MESSAGES['api_error'], parse_mode='Markdown')
        
        # Clear waiting state
        context.user_data.clear()
    
    elif waiting_for == 'video_swap_face':
        # Process video face swap
        quality = 'hd' if user_data.get('premium') else 'standard'
        
        await update.message.reply_text(
            MESSAGES['processing'].format(swap_type="video face swap", time="2-5 minutes"),
            parse_mode='Markdown'
        )
        
        photo_file = await update.message.photo[-1].get_file()
        face_data = await photo_file.download_as_bytearray()
        video_data = context.user_data.get('video_file')
        
        # Process video
        result = await swap_video_api(video_data, face_data, quality)
        
        if result:
            await update.message.reply_video(
                video=result,
                caption="✅ **Video face swap completed!**\n\n💎 Premium users get faster processing and HD quality!"
            )
            update_usage(user_id, 'video')
            logger.info(f"Successful video swap for user {user_id}")
        else:
            await update.message.reply_text(ERROR_MESSAGES['api_error'], parse_mode='Markdown')
        
        context.user_data.clear()
    
    else:
        await update.message.reply_text("📸 **Photo received!**\n\nUse /start to begin face swapping!", parse_mode='Markdown')

async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    waiting_for = context.user_data.get('waiting_for')
    
    logger.info(f"Video received from user {user_id}")
    
    if waiting_for == 'video_swap_video':
        video_duration = update.message.video.duration
        video_size = update.message.video.file_size
        
        # Check limits
        max_duration = PREMIUM_LIMITS['max_video_duration'] if user_data.get('premium') else FREE_LIMITS['max_video_duration']
        max_size = PREMIUM_LIMITS['max_file_size'] if user_data.get('premium') else FREE_LIMITS['max_file_size']
        
        if video_duration > max_duration:
            await update.message.reply_text(
                ERROR_MESSAGES['video_too_long'].format(
                    free_limit=FREE_LIMITS['max_video_duration'],
                    premium_limit=PREMIUM_LIMITS['max_video_duration']
                ),
                parse_mode='Markdown'
            )
            return
        
        if video_size > max_size:
            await update.message.reply_text(
                ERROR_MESSAGES['file_too_large'].format(max_size=max_size // (1024*1024)),
                parse_mode='Markdown'
            )
            return
        
        # Store video
        video_file = await update.message.video.get_file()
        video_data = await video_file.download_as_bytearray()
        context.user_data['video_file'] = video_data
        context.user_data['waiting_for'] = 'video_swap_face'
        
        await update.message.reply_text(f"""✅ **Video received!** ({video_duration}s)

📤 **Now send the face image** you want to swap into the video

🎬 Processing will begin automatically...""", parse_mode='Markdown')
    else:
        await update.message.reply_text("🎥 **Video received!**\n\nUse /start to begin video face swapping!", parse_mode='Markdown')

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    # Check for payment confirmations or admin commands
    if text.startswith('/admin') and update.effective_user.id in ADMIN_IDS:
        await admin_handler(update, context)
    else:
        await update.message.reply_text("""👋 **Hello!**

🤖 **Face Swap Bot Commands:**
/start - Main menu
/premium - Premium plans
/usage - Check your usage

✨ **Ready to swap faces?** Use /start to begin!""", parse_mode='Markdown')

async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin commands handler"""
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    command = update.message.text.lower()
    
    if command == '/admin_stats':
        users = load_users()
        total_users = len(users)
        premium_users = sum(1 for user in users.values() if user.get('premium'))
        total_swaps = sum(user.get('total_swaps', 0) for user in users.values())
        
        stats_text = f"""📊 **Admin Statistics**

👥 **Total Users:** {total_users}
💎 **Premium Users:** {premium_users}
📈 **Total Swaps:** {total_swaps}
📅 **Date:** {date.today()}

💰 **Revenue Estimate:** ₹{premium_users * 299} (monthly avg)"""
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')

async def main():
    logger.info("Starting Face Swap Bot with full features...")
    
    # Start health check web server
    health_app = web.Application()
    health_app.router.add_get('/', health_handler)
    health_app.router.add_get('/health', health_handler)
    
    runner = web.AppRunner(health_app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()
    logger.info(f"Health server started on {HOST}:{PORT}")
    
    # Create bot application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("premium", lambda u, c: button_handler(u, c)))
    application.add_handler(CommandHandler("usage", lambda u, c: button_handler(u, c)))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    application.add_handler(MessageHandler(filters.VIDEO, video_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    # Start the bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    logger.info("Face Swap Bot started successfully!")
    logger.info("Features: Image/Video swap, Premium plans, Usage tracking, Admin panel")
    logger.info("Monetization ready!")
    
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down Face Swap Bot...")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        await site.stop()

if __name__ == "__main__":
    asyncio.run(main())
    
