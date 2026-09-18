import datetime

from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from common.permissions import HasRole, IsAdminOrHR
from recruitment.serializers import HiringRequesDetailSerializer, RecruitmentOverviewSerializer, HiringRequesSerializer
from recruitment.models import JobPosting, Application, HiringRequest, CandidateEmailLog
# Create your views here.

import datetime
from django.utils import timezone
from django.db.models import Count, Q


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR", "TEAM_LEAD"])])
def recruitment_overview(request):
    user = request.user
    role = user.role
    one_week_ago = timezone.now() - datetime.timedelta(days=7)

    # 1. Base QuerySets
    open_jobs = JobPosting.objects.filter(
        status=JobPosting.JobStatus.PUBLISHED)
    pending_requests = HiringRequest.objects.filter(
        status=HiringRequest.RequestStatus.PENDING)
    applications = Application.objects.select_related(
        'candidate', 'job_posting')
    emails = CandidateEmailLog.objects.filter(is_sent_successfully=True)

    # 2. Scope by Department for TEAM_LEAD
    if role == "TEAM_LEAD":
        print("team lead here")
        user_dept = user.department
        open_jobs = open_jobs.filter(department=user_dept)
        pending_requests = pending_requests.filter(department=user_dept)
        applications = applications.filter(job_posting__department=user_dept)
        emails = emails.filter(job_posting__department=user_dept)

    # 3. Aggregations & Metrics
    new_apps_count = applications.filter(created_at__gte=one_week_ago).count()
    emails_count = emails.filter(created_at__gte=one_week_ago).count()

    # 4. Pipeline Funnel (Single DB Query)
    funnel_data = (
        applications
        .values('stage')
        .annotate(total=Count('id'))
    )
    pipeline_funnel_dict = {item['stage']: item['total']
                            for item in funnel_data}

    # 5. Fetch Specific Sub-Lists
    priority_candidates = applications.filter(is_priority=True)

    # 6. Build Payload
    payload = {
        "total_open_jobs": open_jobs.count(),
        "pending_hiring_requests_count": pending_requests.count(),
        "new_applications_this_week": new_apps_count,
        "emails_sent_this_week": emails_count,
        "open_jobs": open_jobs,
        "pending_hiring_requests": pending_requests,
        "priority_candidates": priority_candidates,
        "pipeline_funnel": pipeline_funnel_dict,
    }

    overview_data = RecruitmentOverviewSerializer(payload).data
    return Response(overview_data)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def hiring_request_list(request):
    if request.method == "GET":
        if request.user.role == "TEAM_LEAD":
            hiring_requests = HiringRequest.objects.filter(
                requested_by=request.user)
        else:
            hiring_requests = HiringRequest.objects.all()
        serializer = HiringRequesSerializer(hiring_requests, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        if request.user.role != "TEAM_LEAD":
            return Response({"detail": "Only Team Leads can submit hiring requests."}, status=403)
        serializer = HiringRequesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(requested_by=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated, HasRole(["TEAM_LEAD"])])
def hiring_request_detail(request, pk):
    # 1. Fetch object or return 404
    # 2. Check ownership (request.user == hiring_req.requested_by)
    hiring_request = get_object_or_404(HiringRequest, id=pk)
    if hiring_request.requested_by != request.user:
        return Response({"error": "You are not Authorized to view this"}, status=403)

    if request.method == "GET":
        serializer = HiringRequesDetailSerializer(hiring_request)
        return Response(serializer.data)

    elif request.method in ["PUT", "PATCH"]:
        if hiring_request.status != "PENDING":
            return Response({"error": "Cannot edit an approved/rejected request"}, status=400)
        serializer = HiringRequesDetailSerializer(
            hiring_request, data=request.data, partial=(request.method == "PATCH"))
        if serializer.is_valid():
            updated_instance = serializer.save()
            return Response(HiringRequesDetailSerializer(updated_instance).data)
        return Response(serializer.errors, status=400)

    elif request.method == "DELETE":
        if hiring_request.status != "PENDING":
            return Response({"error": "Cannot edit an approved/rejected request"}, status=400)
        hiring_request.delete()
        return Response(status=204)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def hiring_request_hr_action(request, pk):
    hiring_request = get_object_or_404(HiringRequest, id=pk)

    status = request.data.get("status")
    rejection_reason = request.data.get("rejection_reason", "").strip()

    allowed_statuses = [
        HiringRequest.RequestStatus.APPROVED,
        HiringRequest.RequestStatus.REJECTED,
        HiringRequest.RequestStatus.MORE_INFO,
    ]
    if status not in allowed_statuses:
        return Response(
            {"error": f"Invalid status. Must be one of: {allowed_statuses}"},
            status=400
        )

    if status == HiringRequest.RequestStatus.REJECTED:
        if not rejection_reason:
            return Response(
                {"error": "A rejection_reason is required when rejecting a request."},
                status=400
            )
        hiring_request.rejection_reason = rejection_reason

    hiring_request.status = status
    hiring_request.save(
        update_fields=["status", "rejection_reason"]
        if status == HiringRequest.RequestStatus.REJECTED else ["status"]
    )

    serializer = HiringRequesDetailSerializer(hiring_request)
    return Response(serializer.data, status=200)
