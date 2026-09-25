from datetime import timedelta

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from common.permissions import IsAdminOrHR
from documents.models import DocumentRequest, DocumentTemplate, DocumentTypeConfig
from documents.serializers import (
    DocumentRequestDetailSerializer,
    DocumentRequestSerializer,
    DocumentTemplateSerializer,
    DocumentTypeSerializer,
)
from documents.services import (
    generate_pdf_from_html,
    generate_reference_number,
    get_document_context,
    render_template_to_html,
)
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


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def document_request_detail_view(request, pk):
    if request.user.role in ["ADMIN", "HR"]:
        document_request = get_object_or_404(DocumentRequest.objects.select_related(
            "requested_by", "document_type", "assigned_hr"), id=pk,)
    else:
        document_request = get_object_or_404(DocumentRequest.objects.select_related(
            "requested_by", "document_type", "assigned_hr"), id=pk, requested_by=request.user)
    if request.method == "GET":
        serializer = DocumentRequestDetailSerializer(document_request)
        return Response(serializer.data, status=200)

    if request.method == "DELETE":
        if request.user.role not in ["ADMIN", "HR"]:
            if document_request.status != DocumentRequest.RequestChoice.PENDING:
                return Response(
                    {"error": "Cannot delete/cancel requests that are already in progress or completed."},
                    status=400
                )
        document_request.delete()
        return Response(status=204)

    if request.method in ["PUT", "PATCH"]:
        is_hr = request.user.role in ["HR", "ADMIN"]

        if not is_hr:
            if document_request.status != DocumentRequest.RequestChoice.PENDING:
                return Response({"error": "Cannot edit requests that are already in progress or completed."}, status=400)
            serializer = DocumentRequestDetailSerializer(
                document_request, data=request.data, partial=(request.method == "PATCH"))
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)
        else:
            action = request.data.get("action")
            requested_status = request.data.get("status")

            if action == "pickup" or requested_status == DocumentRequest.RequestChoice.IN_PROGRESS:
                document_request.assigned_hr = request.user
                document_request.status = DocumentRequest.RequestChoice.IN_PROGRESS
                document_request.save()

            elif action == "approve" or requested_status in [DocumentRequest.RequestChoice.READY, "APPROVED"]:
                document_request.assigned_hr = request.user
                document_request.status = DocumentRequest.RequestChoice.READY
                document_request.rejection_reason = ""
                document_request.save()

            elif action == "reject" or requested_status == DocumentRequest.RequestChoice.REJECTED:
                rejection_reason = request.data.get("rejection_reason")
                if not rejection_reason:
                    return Response({"error": "Rejection reason is required when rejecting a request."}, status=400)

                document_request.status = DocumentRequest.RequestChoice.REJECTED
                document_request.rejection_reason = rejection_reason
                document_request.save()

            else:
                serializer = DocumentRequestDetailSerializer(
                    document_request,
                    data=request.data,
                    partial=True
                )
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=200)
                return Response(serializer.errors, status=400)

            serializer = DocumentRequestDetailSerializer(document_request)
            return Response(serializer.data, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminOrHR])
def preview_document_letter_view(request, pk):
    document_request = get_object_or_404(
        DocumentRequest.objects.select_related(
            "requested_by", "document_type"),
        id=pk,
    )
    template = get_object_or_404(
        DocumentTemplate.objects.select_related("document_type"),
        document_type=document_request.document_type,
    )

    rendered_html = render_template_to_html(
        template.body_content,
        get_document_context(document_request),
    )
    return Response({"html": rendered_html, "title": template.title}, status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminOrHR])
def generate_and_issue_document_view(request, pk):
    document_request = get_object_or_404(
        DocumentRequest.objects.select_related(
            "requested_by", "document_type", "assigned_hr"),
        id=pk,
    )
    template = get_object_or_404(
        DocumentTemplate.objects.select_related("document_type"),
        document_type=document_request.document_type,
    )

    uploaded_file = request.FILES.get(
        "generated_file") or request.FILES.get("manual_file")

    if uploaded_file:
        document_request.generated_file.save(
            uploaded_file.name, uploaded_file, save=False)
        document_request.manual_upload = True
        document_request.assigned_hr = request.user
        document_request.status = DocumentRequest.RequestChoice.READY
        if not document_request.reference_number:
            document_request.reference_number = generate_reference_number(
                document_request)
        document_request.file_version = (
            document_request.file_version or 0) + 1
        document_request.save()
        return Response(DocumentRequestDetailSerializer(document_request).data, status=200)

    context_data = get_document_context(document_request)
    rendered_html = render_template_to_html(
        template.body_content,
        context_data,
    )
    pdf_buffer = generate_pdf_from_html(
        rendered_html,
        include_letterhead=bool(template.include_letterhead),
    )

    if not document_request.reference_number:
        document_request.reference_number = generate_reference_number(
            document_request)

    pdf_name = f"{document_request.reference_number}.pdf"
    document_request.generated_file.save(
        pdf_name, ContentFile(pdf_buffer.getvalue()), save=False)

    document_request.manual_upload = False
    document_request.file_version = (document_request.file_version or 0) + 1
    if not document_request.assigned_hr_id:
        document_request.assigned_hr = request.user

    document_request.status = DocumentRequest.RequestChoice.READY
    document_request.save()

    serializer = DocumentRequestDetailSerializer(document_request)
    return Response(serializer.data, status=200)
