from django.urls import path
from recruitment.views import *

urlpatterns = [
    path("overview/", recruitment_overview, name="recruitment_overview"),
    path("hiringreq/", hiring_request, name="hiring_request"),
    path("hiringreq/<int:pk>/", hiring_request_detail,
         name="hiring_request_detail"),
]
