from django.contrib import admin

# Register your models here.
from recruitment.models import *

admin.site.register(HiringRequest)
admin.site.register(JobPosting)
admin.site.register(Candidate)
admin.site.register(Application)
