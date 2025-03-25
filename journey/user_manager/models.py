from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models


class Provider(models.Model):
    domain = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=50)

class User(AbstractUser):
    email = models.EmailField(_('email address'), max_length=255, unique=True)
    nickname = models.CharField(max_length=15, unique=False)
    username = None
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, blank=True)

    # Add Extra user fields here

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']