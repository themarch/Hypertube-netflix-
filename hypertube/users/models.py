from django.db import models
from django.contrib.auth.models import User
from PIL import Image

class Profile(models.Model):
    MY_LANGUAGE = [ ('en', 'English'), ('fr', 'French'), ('it', 'Italian')]
    language = models.CharField(default='en', max_length = 5, choices = MY_LANGUAGE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    already = models.CharField(max_length=300, blank=True)
    token = models.CharField(max_length=300, blank=True, default='')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)