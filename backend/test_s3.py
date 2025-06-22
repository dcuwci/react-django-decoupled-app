#!/usr/bin/env python
"""
Test script to verify S3 connection and upload
"""
import os
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

import boto3
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def test_s3_connection():
    """Test S3 connection and basic operations"""
    print("Testing S3 connection...")
    
    try:
        # Test boto3 client directly
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            verify=settings.AWS_S3_VERIFY,
            use_ssl=settings.AWS_S3_USE_SSL
        )
        
        # List buckets
        buckets = s3_client.list_buckets()
        print(f"✅ S3 connection successful!")
        print(f"Available buckets: {[b['Name'] for b in buckets['Buckets']]}")
        
        # List objects in our bucket
        try:
            response = s3_client.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
            if 'Contents' in response:
                print(f"Objects in bucket '{settings.AWS_STORAGE_BUCKET_NAME}':")
                for obj in response['Contents']:
                    print(f"  - {obj['Key']} ({obj['Size']} bytes)")
            else:
                print(f"Bucket '{settings.AWS_STORAGE_BUCKET_NAME}' is empty")
        except Exception as e:
            print(f"❌ Error listing bucket contents: {e}")
        
        # Test Django storage backend
        print("\nTesting Django storage backend...")
        test_content = ContentFile(b"Hello, S3!", name="test.txt")
        saved_path = default_storage.save("test/test.txt", test_content)
        print(f"✅ File saved to: {saved_path}")
        
        # Verify the file exists
        if default_storage.exists(saved_path):
            print(f"✅ File exists in storage")
            # Get the URL
            url = default_storage.url(saved_path)
            print(f"File URL: {url}")
        else:
            print(f"❌ File not found in storage")
        
        # Clean up test file
        default_storage.delete(saved_path)
        print(f"✅ Test file cleaned up")
        
    except Exception as e:
        print(f"❌ S3 connection failed: {e}")
        print(f"Endpoint: {settings.AWS_S3_ENDPOINT_URL}")
        print(f"Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
        print(f"Storage backend: {settings.DEFAULT_FILE_STORAGE}")

if __name__ == '__main__':
    test_s3_connection()