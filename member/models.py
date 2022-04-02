from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.utils import timezone


def upload_location(profile, filename):
    return '%s/%s' % (profile.user, filename)


class LoggedRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login = models.DateTimeField(default=timezone.now, db_index=True, blank=True, null=True)
    logout = models.DateTimeField(default=timezone.now, db_index=True, blank=True, null=True)
    ip_address = models.CharField(max_length=250)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='static/images/default_author.jpg', upload_to=upload_location)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    about_author = models.TextField(blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, ** kwargs)