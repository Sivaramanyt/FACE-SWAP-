import base64
import requests
import os
from config import RAPIDAPI_KEY

async def swap_faces_api(source_image_data, target_image_data, quality='standard'):
    """Enhanced Face swap with detailed error logging"""
    try:
        print("🔍 DEBUG: Starting face swap...")
        
        # Check API key first
        if not RAPIDAPI_KEY or RAPIDAPI_KEY == 'your_rapidapi_key':
            print("❌ ERROR: No valid RapidAPI key found!")
            print("💡 SOLUTION: Add RAPIDAPI_KEY to Koyeb environment variables")
            return None
        
        print(f"✅ API Key found: {RAPIDAPI_KEY[:10]}...")
        print(f"📊 Source size: {len(source_image_data)} bytes")
        print(f"📊 Target size: {len(target_image_data)} bytes")
        
        # Convert to base64
        source_b64 = base64.b64encode(source_image_data).decode()
        target_b64 = base64.b64encode(target_image_data).decode()
        
        print("✅ Images converted to base64")
        
        # API call
        url = "https://face-swap1.p.rapidapi.com/faceswap"
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
        
        print("📤 Sending request to face swap API...")
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📝 Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            result = response.json()
            if 'result_image' in result:
                print("✅ SUCCESS: Face swap completed!")
                return base64.b64decode(result['result_image'])
            else:
                print("❌ No result_image in response")
                return None
        else:
            print(f"❌ API ERROR: {response.status_code}")
            if response.status_code == 400:
                print("💡 Possible cause: No face detected in images")
            elif response.status_code == 401:
                print("💡 Possible cause: Invalid API key")
            elif response.status_code == 429:
                print("💡 Possible cause: Quota exceeded (used all 10 monthly requests)")
            return None
            
    except Exception as e:
        print(f"💥 EXCEPTION: {str(e)}")
        return None
        
