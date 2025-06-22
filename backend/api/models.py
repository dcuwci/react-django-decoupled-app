from django.db import models
from django.conf import settings

# Import custom storage if LocalStack is enabled
if getattr(settings, 'USE_LOCALSTACK', False):
    from storage_backends import LocalStackS3Storage
    image_storage = LocalStackS3Storage()
else:
    image_storage = None

class Message(models.Model):
    body = models.TextField()

    def __str__(self):
        return self.body

class Image(models.Model):
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(
        upload_to='images/',
        storage=image_storage if image_storage else None
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Image {self.id}"

    class Meta:
        ordering = ['-uploaded_at']
