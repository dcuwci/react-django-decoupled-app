from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, ImageViewSet, serve_s3_image, debug_s3_bucket

router = DefaultRouter()
router.register(r'messages', MessageViewSet)
router.register(r'images', ImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('s3-image/<path:image_path>', serve_s3_image, name='serve_s3_image'),
    path('debug-s3/', debug_s3_bucket, name='debug_s3_bucket'),
]