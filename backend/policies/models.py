from datetime import datetime
import os
from django.conf import settings
from django.db import models
from django.utils.text import slugify


def policy_upload_to(instance, filename):
    """
    Constructs a dynamic file path for uploaded policy files.

    Args:
        instance: The instance of Policy being saved.
        filename: Original filename of the uploaded file.

    Returns:
        A string representing the upload path.
    """
    year = datetime.now().year
    _, file_extension = os.path.splitext(filename)

    # Safely format category and policy titles for path usage
    category_slug = slugify(
        instance.category.name) if instance.category else "uncategorized"
    title_slug = slugify(instance.title) if instance.title else "policy"

    timestamp = int(datetime.now().timestamp())
    new_filename = f"{title_slug}_{timestamp}{file_extension}"

    return f"policy_category/{category_slug}/{year}/{new_filename}"
# Create your models here.


class PolicyCategory(models.Model):
    name = models.CharField(max_length=300)
    description = models.TextField(max_length=1000, blank=True, null=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} is active :{self.is_active}'


class Policy(models.Model):
    category = models.ForeignKey(
        PolicyCategory, on_delete=models.CASCADE, related_name="policies")
    title = models.CharField(max_length=500)
    content = models.TextField(max_length=20000)
    document_file = models.FileField(
        upload_to=policy_upload_to, blank=True, null=True)
    version = models.FloatField(default=1.0)
    is_mandatory = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class PolicyAcknowledgement(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_acknowledgements")
    policy = models.ForeignKey(
        Policy, on_delete=models.CASCADE, related_name="acknowledgements")
    acknowledged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'policy')
