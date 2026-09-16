from django.urls import path

from .views import departments, office_locations

urlpatterns = [
    path("departments/", departments, name="department-list"),
    path("locations/", office_locations, name="location-list"),
]
