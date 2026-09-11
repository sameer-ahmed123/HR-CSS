from django.conf import settings
from django.db import models

from common.models import TimeStampedModel


class Department(TimeStampedModel):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)
    head = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.SET_NULL, related_name="headed_departments")

    def __str__(self):
        return f"{self.name} ({self.code})"


class Designation(TimeStampedModel):
    title = models.CharField(max_length=120)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="designations")

    def __str__(self):
        return self.title


class OfficeLocation(TimeStampedModel):
    name = models.CharField(max_length=120)
    address = models.TextField()
    city = models.CharField(max_length=80)
    country = models.CharField(max_length=80)

    def __str__(self):
        return f"{self.name}, {self.city}"
