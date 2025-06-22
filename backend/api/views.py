from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse, Http404
from django.conf import settings
import boto3
from botocore.exceptions import ClientError
from .models import Message, Image
from .serializers import MessageSerializer, ImageSerializer

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    parser_classes = (MultiPartParser, FormParser)

@api_view(['GET'])
def serve_s3_image(request, image_path):
    """
    Proxy endpoint to serve images from LocalStack S3
    """
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
        
        # Get the object from S3
        response = s3_client.get_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=image_path
        )
        
        # Get content type
        content_type = response.get('ContentType', 'image/jpeg')
        
        # Return the image data
        return HttpResponse(
            response['Body'].read(),
            content_type=content_type
        )
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            raise Http404("Image not found")
        else:
            raise Http404("Error retrieving image")
    except Exception as e:
        raise Http404("Error retrieving image")

@api_view(['GET'])
def debug_s3_bucket(request):
    """
    Debug endpoint to list all objects in the S3 bucket
    """
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
        
        # List all objects in the bucket
        response = s3_client.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        
        objects = []
        if 'Contents' in response:
            for obj in response['Contents']:
                objects.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat()
                })
        
        return Response({
            'bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'endpoint': settings.AWS_S3_ENDPOINT_URL,
            'object_count': len(objects),
            'objects': objects
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'endpoint': settings.AWS_S3_ENDPOINT_URL
        }, status=500)
