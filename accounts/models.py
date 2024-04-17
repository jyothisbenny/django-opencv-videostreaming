from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _


# Create your models here.

class TimeStampedModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(_('created'), auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        abstract = True


class User(AbstractBaseUser, TimeStampedModel):
    name = models.CharField(max_length=128, blank=True, null=True, default='')
    email = models.EmailField(max_length=255, null=True, blank=True, unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
