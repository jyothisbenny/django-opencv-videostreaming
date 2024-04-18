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


class Video(TimeStampedModel):
    name = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)


class Machine(TimeStampedModel):
    machine_name = models.CharField(max_length=255, blank=True, null=True)
    machine_serial_no = models.CharField(max_length=255, blank=True, null=True, unique=True)
    # is_active=False means record is deleted
    is_active = models.BooleanField(default=True)


class ProductionLog(TimeStampedModel):
    cycle_no = models.CharField(max_length=255, blank=True, null=True)
    unique_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    material_name = models.CharField(max_length=255, blank=True, null=True)
    machine = models.ForeignKey(Machine, blank=True, null=True, on_delete=models.CASCADE)
    start_time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            row_count = ProductionLog.objects.count()
            self.invoice_number = 'CN{:03d}'.format(row_count + 1)
        super(ProductionLog, self).save()

    @property
    def duration(self):
        """
        Calculates the duration of production in hours.
        """
        delta = self.end_time - self.start_time
        return delta.total_seconds() / 3600

