from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # keep default fields: username, email, password
    # add any extra fields if needed
    pass

def image_upload_path(instance, filename):
    return f"user_{instance.owner.id}/{filename}"

class ImageItem(models.Model):
    owner = models.ForeignKey("User", related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_upload_path)
    caption = models.TextField(blank=True, null=True)
    original_filename = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_captioned = models.BooleanField(default=False)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.owner.username} - {self.original_filename or self.image.name}"
