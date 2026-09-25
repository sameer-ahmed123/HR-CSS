from django.contrib import admin
from policies.models import *
# Register your models here.
admin.site.register(Policy)
admin.site.register(PolicyCategory)
admin.site.register(PolicyAcknowledgement)
