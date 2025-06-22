from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class LocalStackS3Storage(S3Boto3Storage):
    """
    Custom S3 storage backend for LocalStack
    """
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    region_name = settings.AWS_S3_REGION_NAME
    file_overwrite = settings.AWS_S3_FILE_OVERWRITE
    default_acl = settings.AWS_DEFAULT_ACL
    
    def __init__(self, *args, **kwargs):
        kwargs['bucket_name'] = self.bucket_name
        kwargs['region_name'] = self.region_name
        kwargs['file_overwrite'] = self.file_overwrite
        kwargs['default_acl'] = self.default_acl
        super().__init__(*args, **kwargs)
        
    def _save(self, name, content):
        """Override save to add debugging"""
        print(f"🔄 Saving file to S3: {name}")
        try:
            result = super()._save(name, content)
            print(f"✅ File saved successfully: {result}")
            return result
        except Exception as e:
            print(f"❌ Error saving file to S3: {e}")
            raise
    
    def url(self, name):
        """Override URL to return our proxy URL"""
        # Return the proxy URL instead of direct S3 URL
        return f"/api/s3-image/{name}"