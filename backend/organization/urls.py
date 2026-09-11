from django.urls import path

from .views import DepartmentListCreateView, OfficeLocationListCreateView

urlpatterns = [
    path("departments/", DepartmentListCreateView.as_view(), name="department-list"),
    path("locations/", OfficeLocationListCreateView.as_view(), name="location-list"),
]
