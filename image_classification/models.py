from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Upload(models.Model):
    user = models.ForeignKey('Profile', on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='uploads/')
    predicted_celebrity = models.CharField(max_length=100)
    confidence = models.FloatField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    def set_password(self, raw_password):
        """Set password with hashing."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check password against the hashed password."""
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username