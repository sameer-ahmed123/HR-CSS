import datetime

from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from common.permissions import HasRole, IsAdminOrHR
from recruitment.serializers import HiringRequesDetailSerializer, JobPostingSerializer, RecruitmentOverviewSerializer, HiringRequesSerializer
from recruitment.models import JobPosting, Application, HiringRequest, CandidateEmailLog
# Create your views here.

import datetime
from django.utils import timezone
from django.db.models import Count, Q


def _normalize_bool(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _create_job_posting_for_hiring_request(hiring_request):
    existing_posting = hiring_request.job_postings.first()
    if existing_posting:
        return existing_posting

    job_description = (
        f"{hiring_request.reason}\n\n"
        f"Seniority: {hiring_request.seniority}\n"
        f"Required experience: {hiring_request.required_experience}\n"
        f"Required qualifications: {hiring_request.required_qualifications}"
    )

    return JobPosting.objects.create(
        hiring_request=hiring_request,
        department=hiring_request.department,
        job_title=hiring_request.request_title,
        job_description=job_description,
        required_skills=hiring_request.required_qualifications,
        required_experience=hiring_request.required_experience,
        closing_date=None,
        cv_score_threshold=70,
        status=JobPosting.JobStatus.DRAFT,
    )


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
    create_job_posting = _normalize_bool(
        request.data.get("create_job_posting", False))

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

    if status == HiringRequest.RequestStatus.APPROVED and create_job_posting:
        job_posting = _create_job_posting_for_hiring_request(hiring_request)
        payload = HiringRequesDetailSerializer(hiring_request).data
        payload["job_posting_created"] = True
        payload["job_posting_id"] = job_posting.id
        return Response(payload, status=200)

    serializer = HiringRequesDetailSerializer(hiring_request)
    return Response(serializer.data, status=200)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR", "TEAM_LEAD"])])
def job_posting_list_create(request):
    if request.method == "GET":
        queryset = JobPosting.objects.select_related("department").all()

        # Filtering parameters
        status_param = request.query_params.get("status")
        dept_param = request.query_params.get("department")

        # Team Leads can only see jobs in their department unless filtered
        if request.user.role == "TEAM_LEAD":
            queryset = queryset.filter(department=request.user.department)

        if status_param:
            queryset = queryset.filter(status=status_param)
        if dept_param:
            queryset = queryset.filter(department_id=dept_param)

        serializer = JobPostingSerializer(queryset, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        if request.user.role not in ["ADMIN", "HR"]:
            return Response({"detail": "Only HR and Admins can create job postings."}, status=403)

        serializer = JobPostingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def job_posting_detail(request, pk):
    job = get_object_or_404(JobPosting, id=pk)

    if request.method == "GET":
        serializer = JobPostingSerializer(job)
        return Response(serializer.data)

    elif request.method in ["PUT", "PATCH"]:
        serializer = JobPostingSerializer(
            job, data=request.data, partial=(request.method == "PATCH"))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == "DELETE":
        # Delete allowed only if it is still in DRAFT
        if job.status != JobPosting.JobStatus.DRAFT:
            return Response(
                {"error": "Only draft job postings can be deleted. Close or archive published jobs instead."},
                status=400
            )
        job.delete()
        return Response(status=204)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def job_posting_status_change(request, pk):
    job = get_object_or_404(JobPosting, id=pk)
    target_status = request.data.get("status")

    valid_statuses = [
        JobPosting.JobStatus.PUBLISHED,
        JobPosting.JobStatus.CLOSED,
        JobPosting.JobStatus.DRAFT,
    ]

    if target_status not in valid_statuses:
        return Response({"error": f"Invalid status. Choose from {valid_statuses}"}, status=400)

    job.status = target_status
    job.save(update_fields=["status", "updated_at"])

    return Response(JobPostingSerializer(job).data, status=200)
