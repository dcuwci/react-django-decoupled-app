from rest_framework import serializers
from .models import Message, Image

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Image
        fields = '__all__'
        read_only_fields = ('uploaded_at',)
    
    def get_image_url(self, obj):
        if obj.image and obj.image.name:
            # Return the proxy URL that will serve the image from S3
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'/api/s3-image/{obj.image.name}')
            else:
                return f'/api/s3-image/{obj.image.name}'
        return None