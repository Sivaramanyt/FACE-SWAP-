import json
from datetime import datetime, date

# Simple JSON database for mobile development
users_db = {}

def load_users():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users():
    with open('users.json', 'w') as f:
        json.dump(users_db, f)

def add_user(user_id):
    if str(user_id) not in users_db:
        users_db[str(user_id)] = {
            'premium': False,
            'daily_usage': {
                'date': str(date.today()),
                'image_swaps': 0,
                'video_swaps': 0
            }
        }
        save_users()

def check_user_limits(user_id, swap_type):
    user = users_db.get(str(user_id), {})
    today = str(date.today())
    
    # Reset daily usage if new day
    if user.get('daily_usage', {}).get('date') != today:
        user['daily_usage'] = {
            'date': today,
            'image_swaps': 0,
            'video_swaps': 0
        }
    
    # Check limits
    if user.get('premium', False):
        return True  # Unlimited for premium
    
    usage = user.get('daily_usage', {})
    if swap_type == 'image':
        return usage.get('image_swaps', 0) < 3
    elif swap_type == 'video':
        return usage.get('video_swaps', 0) < 1
    
    return False

def update_usage(user_id, swap_type):
    if str(user_id) in users_db:
        if swap_type == 'image':
            users_db[str(user_id)]['daily_usage']['image_swaps'] += 1
        elif swap_type == 'video':
            users_db[str(user_id)]['daily_usage']['video_swaps'] += 1
        save_users()
