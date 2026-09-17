from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from common.permissions import IsAdminOrHR

from .models import Department, OfficeLocation
from .serializers import DepartmentSerializer, OfficeLocationSerializer


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def departments(request):
    if request.method == "GET":
        queryset = Department.objects.select_related("head").all()
        return Response(DepartmentSerializer(queryset, many=True).data)
    if request.method == "POST":
        if not IsAdminOrHR().has_permission(request, None):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = DepartmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def office_locations(request):
    if request.method == "GET":
        queryset = OfficeLocation.objects.all()
        return Response(OfficeLocationSerializer(queryset, many=True).data)
    if request.method == "POST":
        if not IsAdminOrHR().has_permission(request, None):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = OfficeLocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)
