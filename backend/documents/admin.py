from django.contrib import admin
from documents.models import *
# Register your models here.

admin.site.register(DocumentTemplate)
admin.site.register(DocumentTypeConfig)
admin.site.register(DocumentRequest)
