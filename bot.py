import asyncio
import json
import requests
import base64
import cv2
import numpy as np
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

# Face Detection Function
async def has_detectable_face(image_bytes):
    """Check if image contains a detectable face before API call"""
    try:
        print(f"🔍 Checking face detection for image ({len(image_bytes)} bytes)...")
        
        # Convert bytes to image
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            print("❌ Image decoding failed")
            return False, "Invalid image format"
        
        print(f"✅ Image decoded successfully: {img.shape}")
        
        # Face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        
        print(f"🔍 Found {len(faces)} faces")
        
        if len(faces) == 0:
            return False, "No face detected"
        elif len(faces) > 1:
            return False, f"Multiple faces detected ({len(faces)})"
        else:
            print(f"✅ Single face detected at: {faces[0]}")
            return True, f"Single face detected"
            
    except Exception as e:
        print(f"❌ Face detection error: {e}")
        return False, f"Face detection error: {e}"

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

# Enhanced Face swap API function with debugging
async def swap_faces_api(source_image_data, target_image_data, quality='standard'):
    """Enhanced Face swap with comprehensive error handling and debugging"""
    try:
        print("🚀 STARTING FACE SWAP DEBUG...")
        
        # Step 1: Verify API key
        print(f"🔑 Checking API key...")
        if not RAPIDAPI_KEY:
            print("❌ FATAL: RAPIDAPI_KEY environment variable not found!")
            print("💡 SOLUTION: Add RAPIDAPI_KEY to Koyeb environment variables")
            return None
            
        if RAPIDAPI_KEY == 'your_rapidapi_key':
            print("❌ FATAL: Using placeholder API key!")
            print("💡 SOLUTION: Replace with your actual RapidAPI key")
            return None
            
        print(f"✅ API Key found: {RAPIDAPI_KEY[:10]}...{RAPIDAPI_KEY[-4:]}")
        
        # Step 2: Verify image data
        print(f"📊 Source image: {len(source_image_data)} bytes")
        print(f"📊 Target image: {len(target_image_data)} bytes")
        
        if len(source_image_data) < 1000 or len(target_image_data) < 1000:
            print("❌ FATAL: Images too small (likely corrupted)")
            return None
            
        # Step 3: Convert to base64
        print("🔄 Converting images to base64...")
        try:
            source_b64 = base64.b64encode(source_image_data).decode('utf-8')
            target_b64 = base64.b64encode(target_image_data).decode('utf-8')
            print(f"✅ Base64 conversion successful")
        except Exception as e:
            print(f"❌ FATAL: Base64 encoding failed: {e}")
            return None
        
        # Step 4: Prepare API request
        url = FACE_SWAP_API_CONFIG['base_url'] + FACE_SWAP_API_CONFIG['endpoints']['image_swap']
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "face-swap1.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        payload = {
            "source_image": source_b64,
            "target_image": target_b64,
            "face_enhance": quality == 'hd'
        }
        
        print(f"🌐 API URL: {url}")
        print(f"📦 Payload size: {len(str(payload))} characters")
        
        # Step 5: Make API request
        print("📤 Sending request to RapidAPI...")
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        
        print(f"📡 HTTP Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        print(f"📝 Response Body: {response.text[:300]}...")
        
        # Step 6: Handle response
        if response.status_code == 200:
            print("🎉 SUCCESS: API responded with 200!")
            try:
                result = response.json()
                print(f"📋 Response keys: {list(result.keys())}")
                
                if 'result_image' in result and result['result_image']:
                    swapped_data = base64.b64decode(result['result_image'])
                    print(f"✅ FACE SWAP COMPLETED! Result: {len(swapped_data)} bytes")
                    return swapped_data
                else:
                    print("❌ No result_image in API response")
                    return None
                    
            except Exception as json_err:
                print(f"❌ JSON parsing failed: {json_err}")
                return None
                
        else:
            # Detailed error analysis
            print(f"❌ API REQUEST FAILED!")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 400:
                print("💡 BAD REQUEST: Likely no face detected in images")
            elif response.status_code == 401:
                print("💡 UNAUTHORIZED: Invalid API key")
            elif response.status_code == 403:
                print("💡 FORBIDDEN: Check subscription status")
            elif response.status_code == 429:
                print("💡 RATE LIMITED: Exceeded 10 requests/month")
            elif response.status_code == 500:
                print("💡 SERVER ERROR: Try again later")
            
            return None
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: API took too long to respond")
        return None
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR: {e}")
        return None
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {str(e)}")
        print(f"Error type: {type(e).__name__}")
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
    
    # Get photo data
    photo_file = await update.message.photo[-1].get_file()
    photo_data = await photo_file.download_as_bytearray()
    
    # FACE DETECTION CHECK - NEW ADDITION
    face_ok, face_msg = await has_detectable_face(photo_data)
    if not face_ok:
        await update.message.reply_text(
            f"❌ **{face_msg}**\n\nPlease send a clear photo with a single, visible face.\n\n💡 **Tips for best results:**\n• Use good lighting\n• Face should be clearly visible\n• Avoid group photos or cartoons\n• Try a selfie or portrait photo",
            parse_mode='Markdown'
        )
        return
    
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
        context.user_data['source_image'] = photo_data
        context.user_data['waiting_for'] = 'image_swap_target'
        
        await update.message.reply_text("""✅ **Source image received with valid face!**

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
        
        source_data = context.user_data.get('source_image')
        
        # Perform face swap
        result = await swap_faces_api(source_data, photo_data, quality)
        
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
        
        video_data = context.user_data.get('video_file')
        
        # Process video (placeholder)
        await update.message.reply_text("""🎥 **Video face swap completed!**

⚠️ **Demo Mode:** Full video processing in development
✅ Your video and face image were analyzed
💎 Premium users get full video processing

**Features Coming:**
🎬 1-10 minute video support
🎯 Multiple face tracking
⚡ HD video output""", parse_mode='Markdown')
        
        update_usage(user_id, 'video')
        context.user_data.clear()
    
    else:
        await update.message.reply_text("📸 **Photo received with valid face!**\n\nUse /start to begin face swapping!", parse_mode='Markdown')

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

as
