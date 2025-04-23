from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Upload(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/')
    predicted_celebrity = models.CharField(max_length=100)
    confidence = models.FloatField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username