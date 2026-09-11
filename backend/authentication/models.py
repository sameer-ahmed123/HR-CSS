from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from common.models import TimeStampedModel


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("An email address is required")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", CustomUser.Role.ADMIN)
        if extra_fields.get("is_staff") is not True or extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Superuser must have is_staff and is_superuser set to True")
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser, TimeStampedModel):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        HR = "HR", "HR"
        TEAM_LEAD = "TEAM_LEAD", "Team Lead"
        EMPLOYEE = "EMPLOYEE", "Employee"
        FINANCE = "FINANCE", "Finance"

    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    invited_by = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="invited_users")
    phone_number = models.CharField(max_length=30, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email
