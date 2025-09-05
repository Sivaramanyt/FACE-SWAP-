# Bot Configuration
API_ID = 'YOUR_API_ID'
API_HASH = 'YOUR_API_HASH'
BOT_TOKEN = 'YOUR_BOT_TOKEN'

# Face Swap Settings
FACE_SWAP_CONFIG = {
    'det_size': (640, 640),
    'model_name': 'buffalo_l',
    'quality_levels': ['standard', 'hd', '4k']
}

# User Limits
FREE_LIMITS = {
    'daily_image_swaps': 3,
    'daily_video_swaps': 1,
    'max_video_duration': 30  # seconds
}

PREMIUM_LIMITS = {
    'daily_image_swaps': 999,
    'daily_video_swaps': 999,
    'max_video_duration': 600  # 10 minutes
}
