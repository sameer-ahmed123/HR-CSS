from datetime import datetime
import os
from django.conf import settings
from django.db import models
from django.utils.text import slugify


def policy_upload_to(instance, filename):
    """
    Construct a dynamic storage path for uploaded policy files.

    This keeps each policy document organized by category and year,
    while creating a unique filename for each upload.
    """
    year = datetime.now().year
    _, file_extension = os.path.splitext(filename)

    category_slug = slugify(
        instance.category.name) if instance.category else "uncategorized"
    title_slug = slugify(instance.title) if instance.title else "policy"

    timestamp = int(datetime.now().timestamp())
    new_filename = f"{title_slug}_{timestamp}{file_extension}"

    return f"policy_category/{category_slug}/{year}/{new_filename}"


class PolicyCategory(models.Model):
    name = models.CharField(max_length=300)
    description = models.TextField(max_length=1000, blank=True, null=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} is active : {self.is_active}"


class Policy(models.Model):
    class PolicyStatus(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHED = "PUBLISHED", "Published"
        ARCHIVED = "ARCHIVED", "Archived"

    category = models.ForeignKey(
        PolicyCategory, on_delete=models.CASCADE, related_name="policies")
    title = models.CharField(max_length=500)
    content = models.TextField(max_length=20000)
    document_file = models.FileField(
        upload_to=policy_upload_to, blank=True, null=True)
    version = models.CharField(max_length=20, default="1.0")
    effective_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=PolicyStatus.choices,
        default=PolicyStatus.DRAFT,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_policies",
    )
    is_mandatory = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class PolicyVersionHistory(models.Model):
    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name="version_history",
    )
    version = models.CharField(max_length=20)
    content = models.TextField()
    change_note = models.TextField(blank=True, default="")
    effective_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.policy.title} - {self.version}"


class PolicyAcknowledgement(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_acknowledgements",
    )
    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name="acknowledgements",
    )
    policy_version = models.CharField(max_length=20, default="1.0")
    acknowledged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "policy", "policy_version")

    def __str__(self):
        return f"{self.user.email} acknowledged {self.policy.title} ({self.policy_version})"
