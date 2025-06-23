from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class LocalStackS3Storage(S3Boto3Storage):
    """
    Custom S3 storage backend for LocalStack (Development)
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
        print(f"🔄 Saving file to LocalStack S3: {name}")
        try:
            result = super()._save(name, content)
            print(f"✅ File saved successfully: {result}")
            return result
        except Exception as e:
            print(f"❌ Error saving file to LocalStack S3: {e}")
            raise
    
    def url(self, name):
        """Override URL to return our proxy URL for LocalStack"""
        # Return the proxy URL instead of direct S3 URL
        return f"/api/s3-image/{name}"

class AWSS3Storage(S3Boto3Storage):
    """
    Custom S3 storage backend for AWS S3 (Production)
    """
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    region_name = settings.AWS_S3_REGION_NAME
    file_overwrite = settings.AWS_S3_FILE_OVERWRITE
    default_acl = settings.AWS_DEFAULT_ACL
    location = settings.AWS_LOCATION
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
    
    def __init__(self, *args, **kwargs):
        kwargs['bucket_name'] = self.bucket_name
        kwargs['region_name'] = self.region_name
        kwargs['file_overwrite'] = self.file_overwrite
        kwargs['default_acl'] = self.default_acl
        kwargs['location'] = self.location
        kwargs['custom_domain'] = self.custom_domain
        super().__init__(*args, **kwargs)
        
    def _save(self, name, content):
        """Override save to add debugging"""
        print(f"🔄 Saving file to AWS S3: {name}")
        try:
            result = super()._save(name, content)
            print(f"✅ File saved successfully to AWS S3: {result}")
            return result
        except Exception as e:
            print(f"❌ Error saving file to AWS S3: {e}")
            raise
    
    def url(self, name):
        """Return direct AWS S3 URL or proxy URL based on configuration"""
        if hasattr(settings, 'USE_S3_PROXY') and settings.USE_S3_PROXY:
            # Use proxy URL for additional security/control
            return f"/api/s3-image/{name}"
        else:
            # Return direct AWS S3 URL
            return super().url(name)