#!/usr/bin/env python
"""
Utility script to fix broken S3 links in the database
"""
import os
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

import boto3
from django.conf import settings
from api.models import Image

def fix_broken_s3_links(dry_run=True):
    """
    Fix broken S3 links by removing database records that point to non-existent S3 files
    
    Args:
        dry_run (bool): If True, only show what would be deleted without actually deleting
    """
    print("🔧 Fixing broken S3 links...")
    print(f"🔍 Mode: {'DRY RUN (no changes will be made)' if dry_run else 'LIVE (changes will be applied)'}")
    
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
        
        # Get all S3 files
        print(f"\n📡 Fetching S3 files from bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
        response = s3_client.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        s3_files = set()
        if 'Contents' in response:
            s3_files = {obj['Key'] for obj in response['Contents']}
            print(f"📁 Found {len(s3_files)} files in S3")
        else:
            print("📭 S3 bucket is empty")
        
        # Get all database Image records
        print(f"\n💾 Checking database Image records...")
        all_images = Image.objects.all()
        print(f"📝 Found {all_images.count()} Image records in database")
        
        # Find broken links
        broken_images = []
        valid_images = []
        
        for img in all_images:
            if img.image and img.image.name:
                if img.image.name not in s3_files:
                    broken_images.append(img)
                else:
                    valid_images.append(img)
            else:
                # Image record with no file reference
                broken_images.append(img)
        
        print(f"\n🔗 Link Analysis:")
        print(f"  ✅ Valid links: {len(valid_images)}")
        print(f"  ❌ Broken links: {len(broken_images)}")
        
        if not broken_images:
            print("\n🎉 No broken links found! All database records are valid.")
            return
        
        # Show broken links
        print(f"\n❌ Broken Image records:")
        for img in broken_images:
            file_ref = img.image.name if img.image else "No file reference"
            print(f"  🗑️  ID:{img.id} - '{img.title or 'Untitled'}' -> {file_ref}")
        
        if dry_run:
            print(f"\n🔍 DRY RUN: Would delete {len(broken_images)} broken Image records")
            print("   Run with --fix flag to actually delete these records")
        else:
            # Confirm deletion
            print(f"\n⚠️  WARNING: About to delete {len(broken_images)} Image records!")
            print("   This action cannot be undone.")
            
            confirm = input("   Type 'DELETE' to confirm: ")
            if confirm == 'DELETE':
                deleted_count = 0
                for img in broken_images:
                    try:
                        img_id = img.id
                        img_title = img.title or 'Untitled'
                        img.delete()
                        deleted_count += 1
                        print(f"  🗑️  Deleted: ID:{img_id} - '{img_title}'")
                    except Exception as e:
                        print(f"  ❌ Error deleting ID:{img.id}: {e}")
                
                print(f"\n✅ Successfully deleted {deleted_count} broken Image records")
            else:
                print("\n❌ Deletion cancelled")
        
    except Exception as e:
        print(f"❌ Error during fix operation: {e}")

def clean_orphaned_s3_files(dry_run=True):
    """
    Clean up S3 files that have no corresponding database records
    
    Args:
        dry_run (bool): If True, only show what would be deleted without actually deleting
    """
    print("\n🧹 Cleaning orphaned S3 files...")
    print(f"🔍 Mode: {'DRY RUN (no changes will be made)' if dry_run else 'LIVE (changes will be applied)'}")
    
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
        
        # Get all S3 files
        response = s3_client.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        s3_files = []
        if 'Contents' in response:
            s3_files = [obj['Key'] for obj in response['Contents']]
        
        # Get all database file references
        db_files = set()
        for img in Image.objects.all():
            if img.image and img.image.name:
                db_files.add(img.image.name)
        
        # Find orphaned files
        orphaned_files = [f for f in s3_files if f not in db_files]
        
        print(f"📁 S3 files: {len(s3_files)}")
        print(f"💾 DB references: {len(db_files)}")
        print(f"🗂️ Orphaned files: {len(orphaned_files)}")
        
        if not orphaned_files:
            print("\n🎉 No orphaned S3 files found!")
            return
        
        print(f"\n🗂️ Orphaned S3 files:")
        for file_key in orphaned_files:
            print(f"  🗑️  {file_key}")
        
        if dry_run:
            print(f"\n🔍 DRY RUN: Would delete {len(orphaned_files)} orphaned S3 files")
            print("   Run with --clean-s3 flag to actually delete these files")
        else:
            print(f"\n⚠️  WARNING: About to delete {len(orphaned_files)} S3 files!")
            print("   This action cannot be undone.")
            
            confirm = input("   Type 'DELETE' to confirm: ")
            if confirm == 'DELETE':
                deleted_count = 0
                for file_key in orphaned_files:
                    try:
                        s3_client.delete_object(
                            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                            Key=file_key
                        )
                        deleted_count += 1
                        print(f"  🗑️  Deleted: {file_key}")
                    except Exception as e:
                        print(f"  ❌ Error deleting {file_key}: {e}")
                
                print(f"\n✅ Successfully deleted {deleted_count} orphaned S3 files")
            else:
                print("\n❌ Deletion cancelled")
        
    except Exception as e:
        print(f"❌ Error during S3 cleanup: {e}")

if __name__ == '__main__':
    import sys
    
    if '--fix' in sys.argv:
        fix_broken_s3_links(dry_run=False)
    elif '--clean-s3' in sys.argv:
        clean_orphaned_s3_files(dry_run=False)
    elif '--clean-all' in sys.argv:
        fix_broken_s3_links(dry_run=False)
        clean_orphaned_s3_files(dry_run=False)
    else:
        # Default: dry run for both operations
        fix_broken_s3_links(dry_run=True)
        clean_orphaned_s3_files(dry_run=True)
        
        print(f"\n" + "="*60)
        print("🔧 USAGE:")
        print("  python fix_broken_s3_links.py           # Dry run (show what would be fixed)")
        print("  python fix_broken_s3_links.py --fix     # Fix broken database records")
        print("  python fix_broken_s3_links.py --clean-s3 # Clean orphaned S3 files")
        print("  python fix_broken_s3_links.py --clean-all # Fix both issues")