from django.urls import path
from recruitment.views import *

urlpatterns = [
    path("overview/", recruitment_overview, name="recruitment_overview"),
    path("hiringreq/", hiring_request_list, name="hiring_request"),
    path("hiringreq/<int:pk>/", hiring_request_detail,
         name="hiring_request_detail"),
    path("hiringreq/<int:pk>/status/",
         hiring_request_hr_action, name="hiring_request_staus"),

    path("job-postings/", job_posting_list_create,
         name="job-posting-list-create"),
    path("job-postings/<int:pk>/",
         job_posting_detail, name="job-posting-detail"),
    path("job-postings/<int:pk>/status/",
         job_posting_status_change, name="job-posting-status-change")
]
