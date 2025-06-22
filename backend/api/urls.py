from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, ImageViewSet

router = DefaultRouter()
router.register(r'messages', MessageViewSet)
router.register(r'images', ImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]