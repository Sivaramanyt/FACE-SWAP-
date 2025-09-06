import base64
import requests
import os

async def swap_faces_api(source_image_data, target_image_data, quality='standard'):
    """Enhanced face swap API with comprehensive debug logging"""
    print(f"🚀 FACE SWAP API CALLED!")
    print(f"📊 Source image: {len(source_image_data)} bytes")
    print(f"📊 Target image: {len(target_image_data)} bytes")
    print(f"⚙️ Quality: {quality}")
    
    # Get API key from environment
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', 'your_rapidapi_key')
    
    # Check API key first
    if not RAPIDAPI_KEY or RAPIDAPI_KEY == 'your_rapidapi_key':
        print("❌ ERROR: No valid RapidAPI key found!")
        print(f"🔍 Current RAPIDAPI_KEY value: {repr(RAPIDAPI_KEY)}")
        return None
    
    print(f"✅ API Key found: {RAPIDAPI_KEY[:10]}...{RAPIDAPI_KEY[-4:]}")
    
    try:
        # Convert to base64
        print("🔄 Converting images to base64...")
        source_b64 = base64.b64encode(source_image_data).decode()
        target_b64 = base64.b64encode(target_image_data).decode()
        print(f"✅ Base64 conversion complete")
        
        # API configuration
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
        print(f"🌐 URL: {url}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📝 Response Text: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ SUCCESS: API responded with 200!")
            result = response.json()
            print(f"📋 Response keys: {list(result.keys())}")
            
            if 'result_image' in result:
                print("🎯 Found result_image in response!")
                swapped_data = base64.b64decode(result['result_image'])
                print(f"✅ Face swap completed! Result size: {len(swapped_data)} bytes")
                return swapped_data
            else:
                print("❌ No result_image in response")
                return None
        else:
            print(f"❌ API ERROR! Status: {response.status_code}")
            if response.status_code == 400:
                print("💡 BAD REQUEST: No face detected in images")
            elif response.status_code == 401:
                print("💡 UNAUTHORIZED: Invalid API key")
            elif response.status_code == 403:
                print("💡 FORBIDDEN: Check subscription")
            elif response.status_code == 429:
                print("💡 RATE LIMITED: Exceeded quota")
            return None
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        print(f"🔍 Exception type: {type(e).__name__}")
        return None
                
