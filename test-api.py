#!/usr/bin/env python3
"""
Simple test script to verify the API endpoints are working
Run this after starting the Docker containers
"""

import requests
import json
import sys

API_BASE = "http://localhost:8000/api"

def test_messages():
    """Test the messages API"""
    print("🧪 Testing Messages API...")
    
    try:
        # Test GET messages
        response = requests.get(f"{API_BASE}/messages/")
        if response.status_code == 200:
            print("✅ GET /api/messages/ - Success")
            messages = response.json()
            print(f"   Found {len(messages)} messages")
        else:
            print(f"❌ GET /api/messages/ - Failed ({response.status_code})")
            return False
        
        # Test POST message
        test_message = {"body": "Test message from script"}
        response = requests.post(f"{API_BASE}/messages/", 
                               json=test_message,
                               headers={"Content-Type": "application/json"})
        if response.status_code == 201:
            print("✅ POST /api/messages/ - Success")
            created_message = response.json()
            print(f"   Created message: {created_message['body']}")
        else:
            print(f"❌ POST /api/messages/ - Failed ({response.status_code})")
            print(f"   Response: {response.text}")
            return False
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - Is the backend running on localhost:8000?")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_images():
    """Test the images API"""
    print("\n🧪 Testing Images API...")
    
    try:
        # Test GET images
        response = requests.get(f"{API_BASE}/images/")
        if response.status_code == 200:
            print("✅ GET /api/images/ - Success")
            images = response.json()
            print(f"   Found {len(images)} images")
            for img in images[:3]:  # Show first 3 images
                print(f"   - {img.get('title', 'Untitled')}: {img.get('image_url', 'No URL')}")
        else:
            print(f"❌ GET /api/images/ - Failed ({response.status_code})")
            return False
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - Is the backend running on localhost:8000?")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_s3_debug():
    """Test the S3 debug endpoint"""
    print("\n🧪 Testing S3 Debug Endpoint...")
    
    try:
        response = requests.get(f"{API_BASE}/debug-s3/")
        if response.status_code == 200:
            print("✅ GET /api/debug-s3/ - Success")
            data = response.json()
            print(f"   S3 Bucket: {data.get('bucket')}")
            print(f"   S3 Endpoint: {data.get('endpoint')}")
            print(f"   Object Count: {data.get('object_count', 0)}")
        else:
            print(f"❌ GET /api/debug-s3/ - Failed ({response.status_code})")
            print(f"   Response: {response.text}")
            return False
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - Is the backend running on localhost:8000?")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    print("🚀 Testing React-Django Decoupled App API")
    print("=" * 50)
    
    success_count = 0
    total_tests = 3
    
    if test_messages():
        success_count += 1
    
    if test_images():
        success_count += 1
        
    if test_s3_debug():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! The API is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the Docker containers and logs.")
        print("\nTroubleshooting steps:")
        print("1. Run: docker-compose ps")
        print("2. Run: docker-compose logs backend")
        print("3. Run: docker-compose logs localstack")
        return 1

if __name__ == "__main__":
    sys.exit(main())