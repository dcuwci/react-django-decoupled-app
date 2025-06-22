from django.db import models

class Message(models.Model):
    body = models.TextField()

    def __str__(self):
        return self.body

class Image(models.Model):
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Image {self.id}"

    class Meta:
        ordering = ['-uploaded_at']
