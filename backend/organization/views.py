from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Department, OfficeLocation
from .serializers import DepartmentSerializer, OfficeLocationSerializer


@api_view(["GET", "POST"])
def departments(request):
    if request.method == "GET":
        queryset = Department.objects.select_related("head").all()
        return Response(DepartmentSerializer(queryset, many=True).data)
    serializer = DepartmentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "POST"])
def office_locations(request):
    if request.method == "GET":
        queryset = OfficeLocation.objects.all()
        return Response(OfficeLocationSerializer(queryset, many=True).data)
    serializer = OfficeLocationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)
