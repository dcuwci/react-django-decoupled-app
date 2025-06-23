#!/bin/bash
set -e

echo "Starting Django application initialization..."

# Set AWS environment variables
export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-test}
export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-test}
export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}

# Wait for database
echo "Waiting for database..."
python manage.py migrate --check || python manage.py migrate

# Initialize LocalStack S3 if enabled
if [ "${USE_LOCALSTACK}" = "true" ]; then
    echo "LocalStack integration enabled. Setting up S3..."
    
    # Wait for LocalStack
    for i in {1..30}; do
        if aws --endpoint-url=http://localstack:4566 s3 ls >/dev/null 2>&1; then
            echo "LocalStack is ready"
            break
        fi
        echo "Waiting for LocalStack... ($i/30)"
        sleep 2
    done
    
    # Create bucket if it doesn't exist
    if ! aws --endpoint-url=http://localstack:4566 s3 ls s3://my-test-bucket >/dev/null 2>&1; then
        echo "Creating S3 bucket..."
        aws --endpoint-url=http://localstack:4566 s3 mb s3://my-test-bucket
    fi
fi

echo "Starting Django server..."
exec "$@"