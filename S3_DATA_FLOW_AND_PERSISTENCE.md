# S3 Data Flow and Persistence Guide

## Overview

This document explains the S3 data flow in the React-Django decoupled application and addresses the persistence issue where S3 data doesn't survive container restarts while database records remain intact.

## S3 Data Flow Architecture

### Infrastructure Components

1. **LocalStack**: AWS S3 simulator running on port 4566
2. **PostgreSQL**: Database for storing image metadata
3. **Django Backend**: API server with custom S3 storage backend
4. **React Frontend**: Client application consuming the API

### Data Flow Process

#### Upload Flow
```
Frontend → Django API → LocalStackS3Storage → LocalStack S3 → Database Record
```

1. **Client Upload**: Frontend sends multipart form data to `/api/images/`
2. **Django Processing**: `ImageViewSet` handles upload using `MultiPartParser`
3. **Storage Backend**: `LocalStackS3Storage._save()` processes file with debugging
4. **S3 Storage**: File uploaded to LocalStack bucket (`my-test-bucket`) under `images/` prefix
5. **Database Record**: Image metadata saved to PostgreSQL with S3 path reference

#### Retrieval Flow
```
Frontend → Django API → ImageSerializer → S3 Proxy → LocalStack S3
```

1. **API Request**: Client requests `/api/images/` for image list
2. **Serialization**: `ImageSerializer` adds `image_url` field with proxy URL
3. **Proxy URL**: Returns `/api/s3-image/{path}` instead of direct S3 URL
4. **Image Serving**: `serve_s3_image()` view proxies content from S3
5. **S3 Retrieval**: Boto3 client fetches file from LocalStack
6. **Response**: Image data returned with proper content-type headers

## The Persistence Problem

### Issue Description
When containers are stopped and restarted:
- ✅ **Database records persist** (via `postgres_data` volume)
- ❌ **S3 files are lost** (LocalStack data not properly persisting)
- 💔 **Broken links** between database records and missing S3 files

### Root Cause
The original LocalStack configuration was missing key persistence settings:
- Incomplete snapshot configuration
- Missing proper data directory structure
- No explicit save/load strategy

## Solution Implementation

### 1. Fixed LocalStack Configuration

Updated `docker-compose.yml` with proper persistence settings:

```yaml
localstack:
  image: localstack/localstack:latest
  environment:
    - PERSISTENCE=1
    - SNAPSHOT_SAVE_STRATEGY=ON_SHUTDOWN    # Save state on shutdown
    - SNAPSHOT_LOAD_STRATEGY=ON_STARTUP     # Load state on startup
    - DATA_DIR=/var/lib/localstack/data     # Proper data directory
    - LOCALSTACK_HOST=localstack            # Explicit host setting
  volumes:
    - "localstack_data:/var/lib/localstack" # Persistent volume
```

### 2. Persistence Testing Tools

#### `test_s3_persistence.py`
Comprehensive script to test S3 persistence and detect broken links:

```bash
# Basic persistence test
docker-compose exec backend python test_s3_persistence.py

# Create test image and verify persistence
docker-compose exec backend python test_s3_persistence.py --create-test
```

**Features:**
- Lists all S3 files and database records
- Detects broken links (DB records → missing S3 files)
- Identifies orphaned S3 files (S3 files without DB records)
- Provides detailed integrity report

#### `fix_broken_s3_links.py`
Utility to fix broken links and clean up inconsistencies:

```bash
# Dry run (show what would be fixed)
docker-compose exec backend python fix_broken_s3_links.py

# Fix broken database records
docker-compose exec backend python fix_broken_s3_links.py --fix

# Clean orphaned S3 files
docker-compose exec backend python fix_broken_s3_links.py --clean-s3

# Fix everything
docker-compose exec backend python fix_broken_s3_links.py --clean-all
```

**Features:**
- Safe dry-run mode by default
- Removes database records pointing to missing S3 files
- Cleans up orphaned S3 files
- Confirmation prompts for destructive operations

### 3. Bucket Initialization

The `entrypoint.sh` script ensures the S3 bucket exists on startup:

```bash
# Create bucket if it doesn't exist
if ! aws --endpoint-url=http://localstack:4566 s3 ls s3://my-test-bucket >/dev/null 2>&1; then
    echo "Creating S3 bucket..."
    aws --endpoint-url=http://localstack:4566 s3 mb s3://my-test-bucket
fi
```

## Testing Persistence

### Step-by-Step Test

1. **Start services and create test data:**
   ```bash
   docker-compose up -d
   docker-compose exec backend python test_s3_persistence.py --create-test
   ```

2. **Verify data exists:**
   ```bash
   docker-compose exec backend python test_s3_persistence.py
   ```

3. **Stop and restart containers:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

4. **Verify persistence:**
   ```bash
   docker-compose exec backend python test_s3_persistence.py
   ```

### Expected Results

With the fixed configuration:
- ✅ S3 files persist across container restarts
- ✅ Database records remain intact
- ✅ Links between database and S3 remain valid
- ✅ No broken links or orphaned files

## Key Files and Components

### Configuration Files
- [`docker-compose.yml`](docker-compose.yml) - LocalStack persistence configuration
- [`backend/backend/settings.py`](backend/backend/settings.py) - Django S3 settings

### Storage Backend
- [`backend/storage_backends.py`](backend/storage_backends.py) - Custom S3 storage with debugging

### API Components
- [`backend/api/models.py`](backend/api/models.py) - Image model with S3 storage
- [`backend/api/views.py`](backend/api/views.py) - S3 proxy endpoint and debug views
- [`backend/api/serializers.py`](backend/api/serializers.py) - Image serializer with proxy URLs

### Testing and Maintenance
- [`backend/test_s3_persistence.py`](backend/test_s3_persistence.py) - Persistence testing
- [`backend/fix_broken_s3_links.py`](backend/fix_broken_s3_links.py) - Link repair utility
- [`backend/test_s3.py`](backend/test_s3.py) - Basic S3 connection test

### Initialization
- [`backend/entrypoint.sh`](backend/entrypoint.sh) - Container startup with S3 bucket creation

## Best Practices

### Development Workflow
1. Always test persistence after making changes to LocalStack configuration
2. Run integrity checks periodically: `python test_s3_persistence.py`
3. Use dry-run mode first when fixing broken links
4. Monitor S3 and database consistency

### Production Considerations
- Replace LocalStack with real AWS S3
- Use proper AWS credentials and IAM roles
- Implement proper backup strategies for both database and S3
- Monitor storage costs and cleanup unused files

### Troubleshooting
1. **Container restart loses S3 data**: Check LocalStack persistence configuration
2. **Broken links after restart**: Run `fix_broken_s3_links.py --fix`
3. **Orphaned S3 files**: Run `fix_broken_s3_links.py --clean-s3`
4. **S3 connection issues**: Check LocalStack health and network connectivity

## Migration to Production

To migrate from LocalStack to AWS S3:

1. Update environment variables:
   ```bash
   USE_LOCALSTACK=false
   AWS_S3_ENDPOINT_URL=  # Remove or leave empty
   AWS_ACCESS_KEY_ID=your-aws-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret
   AWS_STORAGE_BUCKET_NAME=your-production-bucket
   ```

2. The same Django storage backend works with both LocalStack and AWS S3
3. Use the same testing and maintenance scripts
4. Ensure proper AWS IAM permissions for S3 operations

## Summary

The S3 persistence issue has been resolved through:
- ✅ Proper LocalStack persistence configuration
- ✅ Comprehensive testing tools
- ✅ Automated link integrity checking
- ✅ Cleanup utilities for broken links
- ✅ Robust error handling and debugging

The data flow now maintains consistency between database records and S3 files across container restarts, providing a reliable development environment that mirrors production behavior.