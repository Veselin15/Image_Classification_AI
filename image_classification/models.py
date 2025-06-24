from django.db import models
from django.contrib.auth.models import User


# The Profile model now links directly to Django's built-in User model.
# This is the standard and recommended way to handle user profiles.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # You can add other profile-specific fields here later, like a profile picture.

    def __str__(self):
        return self.user.username


# The Upload model now correctly links to the User, not the old Profile.
class Upload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='uploads/')
    predicted_celebrity = models.CharField(max_length=100, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Upload by {self.user.username if self.user else 'Guest'} at {self.uploaded_at}"