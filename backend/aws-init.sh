#!/bin/bash

# Exit script on error
set -e

# Set AWS environment variables
export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-test}
export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-test}
export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}

# Only initialize LocalStack if USE_LOCALSTACK is true
if [ "${USE_LOCALSTACK}" = "true" ]; then
  echo "LocalStack integration enabled. Waiting for LocalStack..."
  
  # Wait up to 60 seconds for LocalStack to be ready
  TIMEOUT=60
  COUNTER=0
  while ! aws --endpoint-url=http://localstack:4566 s3 ls &> /dev/null; do
    if [ $COUNTER -ge $TIMEOUT ]; then
      echo "Warning: Timeout waiting for LocalStack to be ready. Starting Django anyway..."
      echo "LocalStack may not be available, but Django will start without S3 functionality."
      break
    fi
    echo "Waiting for LocalStack... ($COUNTER/$TIMEOUT)"
    sleep 3
    COUNTER=$((COUNTER + 3))
  done

  if [ $COUNTER -lt $TIMEOUT ]; then
    echo "LocalStack is ready."
    
    # Create S3 bucket
    BUCKET_NAME="my-test-bucket"
    echo "Checking if bucket $BUCKET_NAME exists..."
    if ! aws --endpoint-url=http://localstack:4566 s3 ls "s3://$BUCKET_NAME" &> /dev/null; then
      echo "Creating bucket: $BUCKET_NAME"
      if aws --endpoint-url=http://localstack:4566 s3 mb "s3://$BUCKET_NAME"; then
        echo "Bucket $BUCKET_NAME created successfully."
      else
        echo "Warning: Failed to create bucket $BUCKET_NAME"
      fi
    else
      echo "Bucket $BUCKET_NAME already exists."
    fi
  fi
else
  echo "LocalStack integration disabled. Skipping LocalStack initialization."
fi

echo "Starting Django application..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
TIMEOUT=30
COUNTER=0
while ! python manage.py migrate --check &> /dev/null; do
  if [ $COUNTER -ge $TIMEOUT ]; then
    echo "Warning: Database not ready after $TIMEOUT seconds. Attempting migrations anyway..."
    break
  fi
  echo "Waiting for database... ($COUNTER/$TIMEOUT)"
  sleep 2
  COUNTER=$((COUNTER + 2))
done

echo "Running database migrations..."
python manage.py migrate
echo "Migrations completed successfully."

# Create S3 bucket if LocalStack is enabled and bucket doesn't exist
if [ "${USE_LOCALSTACK}" = "true" ] && [ $COUNTER -lt $TIMEOUT ]; then
  BUCKET_NAME="my-test-bucket"
  echo "Ensuring S3 bucket $BUCKET_NAME exists..."
  if ! aws --endpoint-url=http://localstack:4566 s3 ls "s3://$BUCKET_NAME" &> /dev/null; then
    echo "Creating S3 bucket: $BUCKET_NAME"
    aws --endpoint-url=http://localstack:4566 s3 mb "s3://$BUCKET_NAME"
    echo "S3 bucket created successfully."
  else
    echo "S3 bucket $BUCKET_NAME already exists."
  fi
fi

# Execute the main command
exec "$@"