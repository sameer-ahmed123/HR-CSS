from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser

# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     ordering = ("email",)
#     list_display = ("email", "first_name", "last_name", "role", "is_active")
#     fieldsets = UserAdmin.fieldsets + \
#         (("HR-CSS profile",
#          {"fields": ("role", "phone_number", "invited_by")}),)
#     add_fieldsets = ((None, {"classes": ("wide",), "fields": (
#         "email", "password1", "password2", "first_name", "last_name", "role")}),)

admin.site.register(CustomUser)