from datetime import timedelta, timezone

from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from common.permissions import HasRole, IsAdminOrHR
from documents.models import DocumentTypeConfig, DocumentTemplate, DocumentRequest
from documents.serializers import DocumentTypeSerializer, DocumentTemplateSerializer, DocumentRequestSerializer
# Create your views here.


@api_view(["GET"])
@permission_classes([AllowAny])
def get_all_docs(request):
    return Response({"Message": "All Docs"})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def document_type_list_create_view(request):
    if request.method == "GET":
        if request.user.role in ["ADMIN", "HR"]:
            doc_types = DocumentTypeConfig.objects.all()
        else:
            doc_types = DocumentTypeConfig.objects.filter(is_active=True)
        serializer = DocumentTypeSerializer(doc_types, many=True)
        return Response(serializer.data, status=200)
    if request.method == "POST":
        if request.user.role not in ["ADMIN", "HR"]:
            return Response({"detail": "Only HR or Admins can create document types."},
                            status=403)
        serializer = DocumentTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdminOrHR])
def document_template_list_create_view(request):
    if request.method == "GET":
        templates = DocumentTemplate.objects.select_related(
            "document_type").all()
        serializer = DocumentTemplateSerializer(templates, many=True)
        return Response(serializer.data, status=200)
    if request.method == "POST":
        doc_type_id = request.data.get("document_type")
        if DocumentTemplate.objects.filter(document_type_id=doc_type_id).exists():
            return Response(
                {"error": "A template already exists for this document type. Use PUT/PATCH to edit it."},
                status=400
            )
        serializer = DocumentTemplateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated, IsAdminOrHR])
def document_type_detail_view(request, pk):
    doc_type = get_object_or_404(DocumentTypeConfig, id=pk)
    if request.method == "GET":
        serializer = DocumentTypeSerializer(doc_type)
        return Response(serializer.data, status=200)

    if request.method == "DELETE":
        doc_type.delete()
        return Response(status=204)

    if request.method in ["PUT", "PATCH"]:
        serializer = DocumentTypeSerializer(
            doc_type, data=request.data, partial=(request.method == "PATCH"))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated, IsAdminOrHR])
def document_template_detail_view(request, pk):
    template = get_object_or_404(DocumentTemplate, id=pk)
    if request.method == "GET":
        serializer = DocumentTemplateSerializer(template)
        return Response(serializer.data, status=200)

    if request.method == "DELETE":
        template.delete()
        return Response(status=204)

    if request.method in ["PUT", "PATCH"]:
        serializer = DocumentTemplateSerializer(
            template, data=request.data, partial=(request.method == "PATCH"))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def document_request_list_create_view(request):
    if request.method == "GET":
        if request.user.role in ["ADMIN", "HR"]:
            queryset = DocumentRequest.objects.select_related(
                "requested_by", "document_type", "assigned_hr").all()
            status_param = request.query_params.get("status")
            doc_type_param = request.query_params.get("document_type")
            requested_by_param = request.query_params.get("requested_by")

            if status_param:
                queryset = queryset.filter(status=status_param)
            if doc_type_param:
                queryset = queryset.filter(document_type_id=doc_type_param)
            if requested_by_param:
                queryset = queryset.filter(requested_by_id=requested_by_param)
        else:
            queryset = DocumentRequest.objects.select_related(
                "document_type", "assigned_hr"
            ).filter(
                requested_by=request.user)
        serializer = DocumentRequestSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    if request.method == "POST":
        serializer = DocumentRequestSerializer(data=request.data)
        if serializer.is_valid():
            doc_type_instance = serializer.validated_data['document_type']
            completion_date = timezone.now().date(
            )+timedelta(days=doc_type_instance.turnaround_days)
            serializer.save(
                requested_by=request.user,
                expected_completion_date=completion_date,
                status=DocumentRequest.RequestChoice.PENDING
            )
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
