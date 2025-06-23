# Production AWS S3 Setup Guide

## Overview

This guide explains how to configure your React-Django decoupled application for production using AWS S3 instead of LocalStack.

## AWS S3 Configuration Steps

### 1. AWS Prerequisites

#### Create AWS S3 Bucket
```bash
# Using AWS CLI
aws s3 mb s3://your-production-bucket-name --region us-east-1

# Or create via AWS Console:
# 1. Go to AWS S3 Console
# 2. Click "Create bucket"
# 3. Enter bucket name: your-production-bucket-name
# 4. Select region: us-east-1 (or your preferred region)
# 5. Configure public access settings as needed
```

#### Create IAM User with S3 Permissions
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-production-bucket-name",
                "arn:aws:s3:::your-production-bucket-name/*"
            ]
        }
    ]
}
```

#### Configure Bucket CORS (if serving images directly)
```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
    }
]
```

### 2. Environment Configuration

#### Update `.env.prod` file:
```bash
# Production Environment Variables
DEBUG=False
SECRET_KEY=your-super-secure-production-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,localhost
DJANGO_ENV=production

# Database
POSTGRES_DB=your_production_db
POSTGRES_USER=your_production_user
POSTGRES_PASSWORD=your_secure_db_password

# AWS S3 Production Configuration
USE_LOCALSTACK=false
USE_AWS_S3=true
AWS_ACCESS_KEY_ID=AKIA...your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_STORAGE_BUCKET_NAME=your-production-bucket-name
AWS_S3_REGION_NAME=us-east-1
USE_S3_PROXY=false  # Set to true if you want to proxy images through Django
```

### 3. Deployment Options

#### Option A: Direct S3 URLs (Recommended for Performance)
- Images served directly from S3
- Faster loading times
- Lower server load
- Set `USE_S3_PROXY=false`

#### Option B: Proxy Through Django
- Images served through Django API
- Better access control
- Consistent domain
- Set `USE_S3_PROXY=true`

## API Endpoints

### Development (LocalStack)
- **Base API**: `http://localhost:8000/api/`
- **Image Upload**: `POST http://localhost:8000/api/images/`
- **Image List**: `GET http://localhost:8000/api/images/`
- **Image Detail**: `GET http://localhost:8000/api/images/{id}/`
- **Image Proxy**: `GET http://localhost:8000/api/s3-image/{image_path}`
- **S3 Debug**: `GET http://localhost:8000/api/debug-s3/`

### Production (AWS S3)
- **Base API**: `https://your-domain.com/api/`
- **Image Upload**: `POST https://your-domain.com/api/images/`
- **Image List**: `GET https://your-domain.com/api/images/`
- **Image Detail**: `GET https://your-domain.com/api/images/{id}/`
- **Image Proxy** (if enabled): `GET https://your-domain.com/api/s3-image/{image_path}`
- **S3 Debug**: `GET https://your-domain.com/api/debug-s3/`

### Image URLs in API Response

#### With Direct S3 URLs (`USE_S3_PROXY=false`)
```json
{
    "id": 1,
    "title": "My Image",
    "image": "media/images/my-image.jpg",
    "image_url": "https://your-bucket.s3.amazonaws.com/media/images/my-image.jpg",
    "uploaded_at": "2025-06-23T13:30:00Z"
}
```

#### With Proxy URLs (`USE_S3_PROXY=true`)
```json
{
    "id": 1,
    "title": "My Image", 
    "image": "media/images/my-image.jpg",
    "image_url": "https://your-domain.com/api/s3-image/media/images/my-image.jpg",
    "uploaded_at": "2025-06-23T13:30:00Z"
}
```

## Frontend Configuration

### Update Frontend Environment
```bash
# .env.production (in frontend directory)
REACT_APP_API_URL=https://your-domain.com
```

### Frontend Image Display
```javascript
// In your React components
const ImageComponent = ({ image }) => {
    return (
        <img 
            src={image.image_url} 
            alt={image.title}
            onError={(e) => {
                console.error('Image failed to load:', image.image_url);
                e.target.src = '/placeholder-image.jpg'; // Fallback
            }}
        />
    );
};
```

## Deployment Commands

### Development (LocalStack)
```bash
# Start development environment
docker-compose up -d

# Test S3 connection
docker-compose exec backend python test_s3.py
```

### Production (AWS S3)
```bash
# Start production environment
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

# Collect static files (if needed)
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

## Storage Backend Differences

### LocalStack (Development)
- **Storage Class**: `LocalStackS3Storage`
- **Endpoint**: `http://localstack:4566`
- **Bucket**: `my-test-bucket`
- **SSL**: Disabled
- **Image URLs**: Always proxied through Django

### AWS S3 (Production)
- **Storage Class**: `AWSS3Storage`
- **Endpoint**: AWS S3 (no custom endpoint)
- **Bucket**: Your production bucket
- **SSL**: Enabled
- **Image URLs**: Direct S3 URLs or proxied (configurable)

## File Organization

### LocalStack Structure
```
my-test-bucket/
├── images/
│   ├── image1.jpg
│   ├── image2.png
│   └── ...
```

### AWS S3 Structure
```
your-production-bucket/
├── media/
│   └── images/
│       ├── image1.jpg
│       ├── image2.png
│       └── ...
```

## Security Considerations

### AWS S3 Bucket Policy (Public Read)
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-production-bucket-name/media/*"
        }
    ]
}
```

### Private Bucket with Proxy
If you want to keep your S3 bucket private and serve images through Django:
1. Set `USE_S3_PROXY=true`
2. Don't add public read policy to bucket
3. Images will be served via `/api/s3-image/{path}`

## Monitoring and Debugging

### Check S3 Configuration
```bash
# In production container
docker-compose -f docker-compose.prod.yml exec backend python -c "
from django.conf import settings
print('USE_AWS_S3:', getattr(settings, 'USE_AWS_S3', False))
print('Bucket:', getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'Not set'))
print('Region:', getattr(settings, 'AWS_S3_REGION_NAME', 'Not set'))
print('Storage Backend:', getattr(settings, 'DEFAULT_FILE_STORAGE', 'Not set'))
"
```

### Test S3 Connection
```bash
# Test AWS S3 connection
docker-compose -f docker-compose.prod.yml exec backend python test_s3.py
```

### Debug S3 Contents
```bash
# List bucket contents via API
curl https://your-domain.com/api/debug-s3/
```

## Migration from LocalStack to AWS S3

### Data Migration
1. Export images from LocalStack
2. Upload to AWS S3 bucket
3. Update database records if needed
4. Test image accessibility

### Configuration Migration
1. Update `.env.prod` with AWS credentials
2. Deploy with production docker-compose
3. Verify S3 integration
4. Test image upload/retrieval

## Troubleshooting

### Common Issues

#### Images not loading
- Check AWS credentials
- Verify bucket permissions
- Check CORS configuration
- Verify image URLs in API response

#### Upload failures
- Check IAM permissions
- Verify bucket exists
- Check AWS region configuration
- Review Django logs

#### CORS errors
- Configure S3 bucket CORS policy
- Check frontend domain in CORS settings
- Verify request headers

### Debug Commands
```bash
# Check Django settings
docker-compose -f docker-compose.prod.yml exec backend python manage.py shell -c "
from django.conf import settings
print('S3 Settings:')
for attr in dir(settings):
    if 'AWS' in attr or 'S3' in attr:
        print(f'{attr}: {getattr(settings, attr, None)}')
"

# Test file upload
docker-compose -f docker-compose.prod.yml exec backend python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
result = default_storage.save('test.txt', ContentFile(b'test'))
print('Upload result:', result)
print('File exists:', default_storage.exists(result))
print('File URL:', default_storage.url(result))
"
```

## Cost Optimization

### S3 Storage Classes
- **Standard**: For frequently accessed images
- **Standard-IA**: For less frequently accessed images
- **Glacier**: For archival storage

### Lifecycle Policies
Configure automatic transitions to cheaper storage classes for older images.

### CloudFront CDN
Consider using AWS CloudFront for global image delivery and caching.

## Summary

The production setup provides:
- ✅ Real AWS S3 integration
- ✅ Scalable file storage
- ✅ Direct S3 URLs or Django proxy options
- ✅ Proper security configurations
- ✅ Production-ready deployment
- ✅ Comprehensive monitoring and debugging tools

Your images will be stored in AWS S3 and served either directly from S3 or through your Django API, depending on your configuration choice.