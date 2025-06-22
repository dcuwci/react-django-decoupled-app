#!/usr/bin/env python
"""
Script to migrate existing local images to LocalStack S3
"""
import os
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.files.storage import default_storage
from api.models import Image
import boto3
from django.conf import settings

def migrate_images_to_s3():
    """Migrate all existing images from local storage to S3"""
    print("Starting migration of images to LocalStack S3...")
    
    # Get all images from database
    images = Image.objects.all()
    migrated_count = 0
    
    for image in images:
        if image.image:
            # Get the local file path
            local_path = image.image.path
            
            if os.path.exists(local_path):
                print(f"Migrating: {image.image.name}")
                
                # Read the file content
                with open(local_path, 'rb') as f:
                    file_content = f.read()
                
                # Save to S3 using Django's storage backend
                # This will automatically use the S3 storage configured in settings
                file_name = image.image.name
                saved_path = default_storage.save(file_name, f)
                
                # Update the image field to point to the S3 location
                image.image.name = saved_path
                image.save()
                
                migrated_count += 1
                print(f"✅ Migrated: {file_name} -> {saved_path}")
            else:
                print(f"❌ Local file not found: {local_path}")
    
    print(f"\n🎉 Migration complete! Migrated {migrated_count} images to LocalStack S3")
    
    # List what's in the S3 bucket
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            verify=settings.AWS_S3_VERIFY,
            use_ssl=settings.AWS_S3_USE_SSL
        )
        
        response = s3_client.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        if 'Contents' in response:
            print(f"\n📁 Files now in S3 bucket '{settings.AWS_STORAGE_BUCKET_NAME}':")
            for obj in response['Contents']:
                print(f"  - {obj['Key']} ({obj['Size']} bytes)")
        else:
            print(f"\n📁 S3 bucket '{settings.AWS_STORAGE_BUCKET_NAME}' is empty")
            
    except Exception as e:
        print(f"❌ Could not list S3 bucket contents: {e}")

if __name__ == '__main__':
    migrate_images_to_s3()