from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Message, Image
from .serializers import MessageSerializer, ImageSerializer

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    parser_classes = (MultiPartParser, FormParser)
