#!/usr/bin/env python
"""
Test script to verify S3 persistence across container restarts
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
from api.models import Image

def test_s3_persistence():
    """Test S3 persistence and database-S3 link integrity"""
    print("🧪 Testing S3 persistence and database-S3 link integrity...")
    
    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            verify=settings.AWS_S3_VERIFY,
            use_ssl=settings.AWS_S3_USE_SSL
        )
        
        print(f"📡 Connected to S3 endpoint: {settings.AWS_S3_ENDPOINT_URL}")
        print(f"🪣 Using bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
        
        # List current S3 contents
        print("\n📁 Current S3 bucket contents:")
        response = s3_client.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        s3_files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                s3_files.append(obj['Key'])
                print(f"  ✅ {obj['Key']} ({obj['Size']} bytes, {obj['LastModified']})")
        else:
            print("  📭 S3 bucket is empty")
        
        # List current database records
        print("\n💾 Current database Image records:")
        db_images = Image.objects.all()
        db_files = []
        if db_images.exists():
            for img in db_images:
                db_files.append(img.image.name)
                print(f"  📝 ID:{img.id} - {img.title or 'Untitled'} -> {img.image.name}")
        else:
            print("  📭 No Image records in database")
        
        # Check for broken links
        print("\n🔗 Checking database-S3 link integrity:")
        broken_links = []
        for img in db_images:
            if img.image.name and img.image.name not in s3_files:
                broken_links.append(img)
                print(f"  ❌ BROKEN: ID:{img.id} -> {img.image.name} (file missing in S3)")
            elif img.image.name:
                print(f"  ✅ VALID: ID:{img.id} -> {img.image.name}")
        
        # Check for orphaned S3 files
        print("\n🗂️ Checking for orphaned S3 files:")
        orphaned_files = []
        for s3_file in s3_files:
            if s3_file not in db_files:
                orphaned_files.append(s3_file)
                print(f"  🔍 ORPHANED: {s3_file} (no database record)")
            else:
                print(f"  ✅ LINKED: {s3_file}")
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"  📁 S3 files: {len(s3_files)}")
        print(f"  💾 DB records: {db_images.count()}")
        print(f"  ❌ Broken links: {len(broken_links)}")
        print(f"  🗂️ Orphaned files: {len(orphaned_files)}")
        
        if broken_links:
            print(f"\n⚠️  WARNING: {len(broken_links)} database records have broken S3 links!")
            print("   Run 'python fix_broken_s3_links.py' to clean up broken records")
        
        if orphaned_files:
            print(f"\n⚠️  WARNING: {len(orphaned_files)} S3 files have no database records!")
            print("   These files are taking up storage space unnecessarily")
        
        if not broken_links and not orphaned_files:
            print("\n✅ All database records and S3 files are properly linked!")
        
        return {
            's3_files': len(s3_files),
            'db_records': db_images.count(),
            'broken_links': len(broken_links),
            'orphaned_files': len(orphaned_files)
        }
        
    except Exception as e:
        print(f"❌ Error during persistence test: {e}")
        return None

def create_test_image():
    """Create a test image to verify persistence"""
    print("\n🖼️ Creating test image for persistence verification...")
    
    try:
        # Create test image content
        test_content = b'Test image content for persistence verification - created at ' + str(os.urandom(8).hex()).encode()
        test_file = ContentFile(test_content, name='persistence-test.jpg')
        
        # Create Image record
        img = Image.objects.create(
            title=f"Persistence Test Image",
            image=test_file
        )
        
        print(f"✅ Created test image: ID:{img.id} -> {img.image.name}")
        return img
        
    except Exception as e:
        print(f"❌ Error creating test image: {e}")
        return None

if __name__ == '__main__':
    # Run persistence test
    result = test_s3_persistence()
    
    # Optionally create a test image
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--create-test':
        create_test_image()
        print("\n" + "="*50)
        print("Re-running test after creating test image:")
        test_s3_persistence()