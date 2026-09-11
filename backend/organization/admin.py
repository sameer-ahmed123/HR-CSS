from django.contrib import admin

from .models import Department, Designation, OfficeLocation

admin.site.register((Department, Designation, OfficeLocation))
