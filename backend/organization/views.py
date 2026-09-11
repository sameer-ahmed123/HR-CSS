from rest_framework import generics

from .models import Department, OfficeLocation
from .serializers import DepartmentSerializer, OfficeLocationSerializer


class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.select_related("head").all()
    serializer_class = DepartmentSerializer


class OfficeLocationListCreateView(generics.ListCreateAPIView):
    queryset = OfficeLocation.objects.all()
    serializer_class = OfficeLocationSerializer
