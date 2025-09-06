import base64
import requests
import os
from config import RAPIDAPI_KEY, FACE_SWAP_API_CONFIG

async def swap_faces_api(source_image_data, target_image_data, quality='standard'):
    """
    Enhanced Face swap using RapidAPI with comprehensive error handling
    
    Args:
        source_image_data (bytes): Source image data (face to use)
        target_image_data (bytes): Target image data (face to replace)
        quality (str): 'standard' or 'hd' for output quality
    
    Returns:
        bytes or None: Swapped image data if successful, None if failed
    """
    try:
        print(f"🔍 Starting face swap API call...")
        print(f"📊 Source image size: {len(source_image_data)} bytes")
        print(f"📊 Target image size: {len(target_image_data)} bytes")
        print(f"⚙️ Quality setting: {quality}")
        
        # Validate API key
        if not RAPIDAPI_KEY or RAPIDAPI_KEY == 'your_rapidapi_key':
            print("❌ ERROR: No valid RapidAPI key found!")
            print("💡 Add your RapidAPI key to Koyeb environment variables: RAPIDAPI_KEY=your_key")
            return None
        
        print(f"🔑 API Key status: {'Valid' if len(RAPIDAPI_KEY) > 20 else 'Invalid'}")
        
        # Convert images to base64
        print("🔄 Converting images to base64...")
        source_b64 = base64.b64encode(source_image_data).decode('utf-8')
        target_b64 = base64.b64encode(target_image_data).decode('utf-8')
        
        print(f"📏 Base64 sizes - Source: {len(source_b64)}, Target: {len(target_b64)}")
        
        # API configuration
        url = FACE_SWAP_API_CONFIG['base_url'] + FACE_SWAP_API_CONFIG['endpoints']['image_swap']
        print(f"🌐 API URL: {url}")
        
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
        
        print("📤 Sending request to Face Swap API...")
        
        # Make API request with timeout
        response = requests.post(
            url, 
            json=payload, 
            headers=headers, 
            timeout=FACE_SWAP_API_CONFIG['timeout']
        )
        
        print(f"📡 Response Status Code: {response.status_code}")
        print(f"📝 Response Headers: {dict(response.headers)}")
        
        # Handle response
        if response.status_code == 200:
            print("✅ API request successful!")
            
            try:
                result = response.json()
                print(f"📋 Response keys: {list(result.keys())}")
                
                result_image_b64 = result.get('result_image')
                if result_image_b64:
                    print("🎯 Face swap result found, decoding...")
                    # Decode base64 image back to bytes
                    swapped_image = base64.b64decode(result_image_b64)
                    print(f"✅ Face swap successful! Result size: {len(swapped_image)} bytes")
                    return swapped_image
                else:
                    print("❌ No result_image in API response")
                    print(f"📝 Full response: {response.text[:500]}...")
                    return None
                    
            except ValueError as json_err:
                print(f"❌ JSON parsing error: {json_err}")
                print(f"📝 Raw response: {response.text[:500]}...")
                return None
                
        else:
            # Handle API errors
            print(f"❌ API Error - Status: {response.status_code}")
            print(f"📝 Error response: {response.text}")
            
            # Common error interpretations
            if response.status_code == 400:
                print("💡 Possible causes: Invalid image format, no face detected, corrupted data")
            elif response.status_code == 401:
                print("💡 Authentication failed - check your RapidAPI key")
            elif response.status_code == 403:
                print("💡 Access forbidden - check subscription status or quota")
            elif response.status_code == 429:
                print("💡 Rate limit exceeded - you've used your monthly quota")
            elif response.status_code == 500:
                print("💡 Server error - try again in a few minutes")
            
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - API took too long to respond")
        return None
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - check internet connection")
        return None
        
    except Exception as e:
        print(f"❌ Unexpected error in face swap: {str(e)}")
        print(f"🔍 Error type: {type(e).__name__}")
        return None

# Alternative simpler version for testing
async def swap_faces_api_simple(source_image_data, target_image_data, quality='standard'):
    """Simplified version for quick testing"""
    try:
        # Convert to base64
        source_b64 = base64.b64encode(source_image_data).decode()
        target_b64 = base64.b64encode(target_image_data).decode()
        
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
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if 'result_image' in result:
                return base64.b64decode(result['result_image'])
        
        return None
        
    except Exception as e:
        print(f"Face swap error: {e}")
        return None
        
