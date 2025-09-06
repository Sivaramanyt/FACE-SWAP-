import os

# Bot Configuration
BOT_TOKEN = "8261755198:AAFikWiiAzIuRN_p8UmAtWslhhy18ia2TBg"
API_ID = os.getenv('29542645')
API_HASH = os.getenv('06e505b8418565356ae79365df5d69e0')
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', '20ec46982dmsh0b6132b905f7ec8p169950jsneeab9433363f')

# Server Configuration
PORT = int(os.getenv('PORT', 8080))  # Your default port
HOST = '0.0.0.0'

# Database Configuration
USERS_FILE = 'users.json'
ADMIN_IDS = [1206988513]  # Your Telegram user ID for admin access

# Face Swap API Configuration
FACE_SWAP_API_CONFIG = {
    'base_url': 'https://face-swap1.p.rapidapi.com',
    'endpoints': {
        'image_swap': '/faceswap',
        'video_swap': '/video-faceswap'
    },
    'headers': {
        'X-RapidAPI-Host': 'face-swap1.p.rapidapi.com',
        'Content-Type': 'application/json'
    },
    'timeout': 60,  # seconds
    'max_retries': 3
}

# User Limits Configuration
FREE_LIMITS = {
    'daily_image_swaps': 3,
    'daily_video_swaps': 1,
    'max_video_duration': 60,  # seconds
    'max_file_size': 50 * 1024 * 1024,  # 50MB
    'quality': 'standard'
}

PREMIUM_LIMITS = {
    'daily_image_swaps': 999,  # Unlimited
    'daily_video_swaps': 999,  # Unlimited
    'max_video_duration': 600,  # 10 minutes
    'max_file_size': 200 * 1024 * 1024,  # 200MB
    'quality': 'hd'
}

# Pricing Configuration
PRICING = {
    'weekly': {
        'price': 99,
        'currency': '₹',
        'duration_days': 7
    },
    'monthly': {
        'price': 299,
        'currency': '₹',
        'duration_days': 30
    },
    'yearly': {
        'price': 1999,
        'currency': '₹',
        'duration_days': 365
    }
}

# Payment Configuration
PAYMENT_CONFIG = {
    'upi_id': 'your_upi_id@paytm',  # Replace with your UPI ID
    'gpay_number': 'your_gpay_number@paytm',
    'phonepe_number': 'your_phonepe_number@ybl',
    'support_username': '@your_username',  # Your Telegram username
    'payment_timeout': 3600  # 1 hour to complete payment
}

# Messages Configuration
MESSAGES = {
    'welcome': """🤖 **Face Swap Bot**

✅ **Bot is fully operational!**
{premium_status} **User**

**Daily Usage:**
📸 Image Swaps: {image_status}
🎥 Video Swaps: {video_status}
📈 Total Swaps: {total_swaps}

**User ID:** `{user_id}`

Choose your swap type:""",

    'premium_features': """💎 **Premium Features**

🚀 **Unlimited Face Swaps**
📸 Unlimited image swaps daily
🎥 Unlimited video swaps daily (up to 10 minutes)
⚡ Priority processing (faster results)
🎯 HD quality output
❌ No watermarks
🎨 Advanced face enhancement

**Pricing:**
• Weekly: ₹99
• Monthly: ₹299 (Save 25%)
• Yearly: ₹1,999 (Save 80%)

Choose your plan:""",

    'image_swap_start': """📸 **Image Face Swap**

🔹 **Step 1:** Send the **source image** (face you want to use)
🔹 **Step 2:** I'll ask for the **target image** (face to replace)
🔹 **Step 3:** Get your swapped result!

📤 **Send the first image now...**""",

    'video_swap_start': """🎥 **Video Face Swap**

🔹 **Step 1:** Send your **video** (up to 1 minute)
🔹 **Step 2:** Send the **face image** to swap
🔹 **Step 3:** Get your face-swapped video!

📤 **Send your video now...**""",

    'limit_reached': """❌ **Daily {swap_type} Swap Limit Reached**

Used: {status}
💎 Upgrade to **Premium** for unlimited swaps!

/premium - See premium options""",

    'processing': """🔄 **Processing {swap_type}...**

This may take {time}...""",

    'payment_instructions': """💳 **Payment for {plan} Plan**

**Amount:** {price}

**Payment Methods:**
📱 GPay: `{gpay_number}`
📱 PhonePe: `{phonepe_number}`
🏦 UPI: `{upi_id}`

**Instructions:**
1. Pay {price} to above UPI ID
2. Send screenshot of payment
3. Get instant premium activation!

**Support:** {support_username}"""
}

# Error Messages
ERROR_MESSAGES = {
    'api_error': "❌ **Processing failed!**\n\nPlease try again in a few minutes.",
    'file_too_large': "❌ **File too large!**\n\nMax size: {max_size}MB",
    'video_too_long': "⚠️ **Video too long!**\n\nFree users: Max {free_limit}s\n💎 Premium users: Up to {premium_limit}s\n\nUpgrade to Premium or send shorter video.",
    'no_face_detected': "❌ **No face detected!**\n\nPlease send a clear image with visible face.",
    'invalid_format': "❌ **Invalid file format!**\n\nSupported: JPG, PNG, MP4, AVI",
    'daily_limit': "⚠️ **Daily limit reached!**\n\n💎 Upgrade to Premium for unlimited usage.",
    'server_error': "❌ **Server error!**\n\nOur team has been notified. Please try again later."
}

# File Configuration
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.webp']
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv']

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'face_swap_bot.log',
    'max_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# Feature Flags
FEATURES = {
    'image_swap': True,
    'video_swap': True,
    'premium_plans': True,
    'payment_processing': True,
    'usage_analytics': True,
    'admin_panel': True,
    'referral_system': False,  # Coming soon
    'batch_processing': False  # Coming soon
}

# Admin Commands
ADMIN_COMMANDS = {
    'stats': '/admin_stats',
    'users': '/admin_users',
    'premium': '/admin_premium',
    'broadcast': '/admin_broadcast'
}

# Analytics Configuration
ANALYTICS_CONFIG = {
    'track_usage': True,
    'track_errors': True,
    'daily_reports': True,
    'user_retention': True
}

# Cache Configuration
CACHE_CONFIG = {
    'user_session_timeout': 300,  # 5 minutes
    'api_cache_timeout': 60,  # 1 minute
    'file_cache_timeout': 1800  # 30 minutes
}
