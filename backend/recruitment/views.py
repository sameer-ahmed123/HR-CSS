import datetime
import logging
import mimetypes

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from common.permissions import HasRole
from recruitment.serializers import (
    ApplicationDetailSerializer,
    ApplicationListSerializer,
    BulkStageUpdateSerializer,
    CandidateEmailLogSerializer,
    CandidateNoteSerializer,
    CandidatePipelineListSerializer,
    CVScoreBreakdownSerializer,
    EmailPreviewSerializer,
    EmailTemplateSerializer,
    HiringRequesDetailSerializer,
    JobApplicationSubmitSerializer,
    JobPostingSerializer,
    PublicJobPostingSerializer,
    RecruitmentOverviewSerializer,
    SendEmailPayloadSerializer,
    HiringRequesSerializer,
)
from recruitment.services import (
    create_job_posting_for_hiring_request,
    normalize_bool,
    render_email_template,
    score_application,
    send_stage_email,
)
from recruitment.models import (
    Application,
    ApplicationStageHistory,
    Candidate,
    CandidateEmailLog,
    CandidateNote,
    CVScore,
    EmailTemplate,
    HiringRequest,
    JobPosting,
)
# Create your views here.

logger = logging.getLogger(__name__)


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


@api_view(["GET"])
@permission_classes([AllowAny])
def public_job_list(request):
    queryset = JobPosting.objects.filter(
        status=JobPosting.JobStatus.PUBLISHED
    ).select_related("department")

    title = request.query_params.get("title")
    department = request.query_params.get("department")
    department_id = request.query_params.get("department_id")

    if title:
        queryset = queryset.filter(job_title__icontains=title)
    if department:
        queryset = queryset.filter(department__name__icontains=department)
    if department_id:
        queryset = queryset.filter(department_id=department_id)

    serializer = PublicJobPostingSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def public_job_detail(request, job_id):
    job = get_object_or_404(
        JobPosting.objects.filter(
            status=JobPosting.JobStatus.PUBLISHED).select_related("department"),
        id=job_id,
    )
    serializer = PublicJobPostingSerializer(job)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def public_job_apply(request, job_id):
    job = get_object_or_404(
        JobPosting.objects.filter(status=JobPosting.JobStatus.PUBLISHED),
        id=job_id,
    )

    serializer = JobApplicationSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    validated = serializer.validated_data
    full_name = validated["full_name"].strip()
    email = validated["email"].strip().lower()
    phone = (validated.get("phone") or "").strip()
    address = (validated.get("address") or "").strip()
    cover_letter = (validated.get("cover_letter") or "").strip()
    links = validated.get("links") or []
    cv_file = validated["cv"]

    candidate = Candidate.objects.filter(email__iexact=email).first()
    if candidate is None:
        candidate = Candidate.objects.create(
            candidate_name=full_name,
            email=email,
            phone_number=phone,
            candidate_skills=str(links) if links else "",
            location=address,
            about=cover_letter,
        )
    else:
        changed = False
        if phone and not candidate.phone_number:
            candidate.phone_number = phone
            changed = True
        if address and not candidate.location:
            candidate.location = address
            changed = True
        if cover_letter and not candidate.about:
            candidate.about = cover_letter
            changed = True
        if links:
            candidate.candidate_skills = str(links)
            changed = True
        if changed:
            candidate.save()

    if Application.objects.filter(candidate=candidate, job_posting=job).exists():
        return Response(
            {"error": "You have already applied for this position."},
            status=400,
        )

    application = Application.objects.create(
        candidate=candidate,
        job_posting=job,
        attached_cv=cv_file,
        stage=Application.Stage.NEW,
        ats_score=0,
        score_reasons={},
        is_priority=False,
    )
    score_application(application)

    subject = f"Thank you for applying for {job.job_title}"
    message = (
        f"Hi {full_name},\n\n"
        f"Thank you for applying for the {job.job_title} position at {job.department.name} HR-CSS. "
        "We have received your application and will review it shortly.\n\n"
        "Best regards,\n"
        "HR Team"
    )

    sent_successfully = True
    error_message = ""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as exc:
        sent_successfully = False
        error_message = str(exc)
        logger.exception(
            "Failed to send application confirmation email to %s", email)

    CandidateEmailLog.objects.create(
        candidate=candidate,
        job_posting=job,
        sent_by=None,
        subject=subject,
        body=message,
        is_sent_successfully=sent_successfully,
        error_message=error_message,
    )

    return Response(
        {
            "message": "Application submitted successfully.",
            "application_id": application.id,
        },
        status=201,
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def hiring_request_hr_action(request, pk):
    hiring_request = get_object_or_404(HiringRequest, id=pk)

    status = request.data.get("status")
    rejection_reason = request.data.get("rejection_reason", "").strip()
    create_job_posting = normalize_bool(
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
        job_posting = create_job_posting_for_hiring_request(hiring_request)
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
        if request.user.role == "TEAM_LEAD":
            department_id = request.data.get("department")
            if department_id is None or int(department_id) != request.user.department_id:
                return Response({"detail": "Team Leads can only create job postings in their own department."}, status=403)
        elif request.user.role not in ["ADMIN", "HR"]:
            return Response({"detail": "Only HR, Admins, and Team Leads can create job postings."}, status=403)

        serializer = JobPostingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def job_posting_detail(request, pk):
    job = get_object_or_404(JobPosting, id=pk)

    if request.method == "GET":
        if request.user.role == "TEAM_LEAD" and request.user.department != job.department:
            return Response({"error": "You do not have access to this job posting."}, status=403)
        serializer = JobPostingSerializer(job)
        return Response(serializer.data)

    if request.user.role == "TEAM_LEAD":
        if request.user.department_id != job.department_id:
            return Response({"detail": "Team Leads can only edit job postings in their own department."}, status=403)
        if job.status != JobPosting.JobStatus.DRAFT:
            return Response({"detail": "Team Leads can only edit draft job postings."}, status=403)
    elif request.user.role not in ["ADMIN", "HR"]:
        return Response({"detail": "Only HR, Admins, and Team Leads can edit job postings."}, status=403)

    if request.method in ["PUT", "PATCH"]:
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


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR", "TEAM_LEAD"])])
def job_posting_applications(request, pk):
    job = get_object_or_404(JobPosting, id=pk)

    if request.user.role == "TEAM_LEAD" and request.user.department != job.department:
        return Response({"error": "You do not have access to this job posting."}, status=403)

    applications = job.applications.select_related(
        "candidate").order_by("-created_at")
    serializer = ApplicationListSerializer(applications, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR", "TEAM_LEAD"])])
def job_posting_application_detail(request, pk, application_id):
    job = get_object_or_404(JobPosting, id=pk)

    if request.user.role == "TEAM_LEAD" and request.user.department != job.department:
        return Response({"error": "You do not have access to this job posting."}, status=403)

    application = get_object_or_404(
        job.applications.select_related("candidate", "job_posting"),
        id=application_id,
    )
    serializer = ApplicationDetailSerializer(application)
    return Response(serializer.data)


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


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def run_cv_scoring_detail(request, application_id):
    application = get_object_or_404(Application.objects.select_related(
        "candidate", "job_posting"), id=application_id)
    result = score_application(application)
    return Response(CVScoreBreakdownSerializer(CVScore.objects.get(application=application)).data | {"is_priority": result["is_priority"]}, status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def rescore_job_applications_bulk(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id)
    applications = Application.objects.filter(
        job_posting=job).select_related("candidate", "job_posting")
    results = []
    for application in applications:
        results.append(score_application(application))
    return Response({"job_id": job.id, "scored_count": len(results), "results": results}, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR", "TEAM_LEAD"])])
def candidate_pipeline_list_view(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id)
    if request.user.role == "TEAM_LEAD" and request.user.department != job.department:
        return Response({"error": "You do not have access to this job posting."}, status=403)

    queryset = Application.objects.filter(job_posting=job).select_related(
        "candidate", "job_posting").prefetch_related("notes", "stage_history")
    stage = request.query_params.get("stage")
    q = request.query_params.get("q")
    if stage:
        queryset = queryset.filter(stage=stage)
    if q:
        queryset = queryset.filter(
            Q(candidate__candidate_name__icontains=q) | Q(candidate__email__icontains=q))

    queryset = queryset.order_by("-ats_score", "-is_priority", "-created_at")
    serializer = CandidatePipelineListSerializer(queryset, many=True)
    return Response(serializer.data, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR", "TEAM_LEAD"])])
def candidate_pipeline_list(request, job_id):
    return candidate_pipeline_list_view(request, job_id)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def update_application_stage_view(request, application_id):
    application = get_object_or_404(Application.objects.select_related(
        "candidate", "job_posting"), id=application_id)
    new_stage = request.data.get("new_stage")
    allowed_stages = [
        Application.Stage.NEW,
        Application.Stage.REVIEWED,
        Application.Stage.SHORTLISTED,
        Application.Stage.TEST_SENT,
        Application.Stage.INTERVIEW,
        Application.Stage.OFFER,
        Application.Stage.HIRED,
        Application.Stage.REJECTED,
    ]
    if new_stage not in allowed_stages:
        return Response({"error": "Invalid stage value."}, status=400)

    old_stage = application.stage
    application.stage = new_stage
    application.save(update_fields=["stage", "updated_at"])

    ApplicationStageHistory.objects.create(
        application=application,
        old_stage=old_stage,
        new_stage=new_stage,
        changed_by=request.user,
    )

    if old_stage != new_stage:
        send_stage_email(application, new_stage, sent_by=request.user)

    serializer = ApplicationDetailSerializer(application)
    return Response(serializer.data, status=200)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def update_candidate_stage(request, application_id):
    return update_application_stage_view(request, application_id)


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def add_candidate_note_view(request, application_id):
    application = get_object_or_404(Application.objects.select_related(
        "candidate", "job_posting"), id=application_id)
    text = (request.data.get("text") or "").strip()
    if not text:
        return Response({"error": "Note text is required."}, status=400)

    note = CandidateNote.objects.create(
        application=application,
        author=request.user,
        text=text,
    )
    serializer = CandidateNoteSerializer(note)
    return Response(serializer.data, status=201)


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def add_candidate_note(request, application_id):
    return add_candidate_note_view(request, application_id)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def bulk_update_stage_view(request):
    serializer = BulkStageUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    applications = Application.objects.filter(
        id__in=serializer.validated_data["application_ids"]).select_related("candidate")
    new_stage = serializer.validated_data["new_stage"]
    for application in applications:
        old_stage = application.stage
        application.stage = new_stage
        application.save(update_fields=["stage", "updated_at"])
        ApplicationStageHistory.objects.create(
            application=application,
            old_stage=old_stage,
            new_stage=new_stage,
            changed_by=request.user,
        )
        if old_stage != new_stage:
            send_stage_email(application, new_stage, sent_by=request.user)

    return Response({"updated_count": applications.count(), "new_stage": new_stage}, status=200)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def bulk_update_candidate_stage(request):
    return bulk_update_stage_view(request)


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR", "TEAM_LEAD"])])
def application_cv_download(request, application_id):
    application = get_object_or_404(
        Application.objects.select_related("candidate", "job_posting"),
        id=application_id,
    )

    if request.user.role == "TEAM_LEAD" and request.user.department != application.job_posting.department:
        return Response({"error": "You do not have access to this application."}, status=403)

    if not application.attached_cv or not application.attached_cv.name:
        return Response({"error": "No CV uploaded for this application."}, status=404)

    file_name = application.attached_cv.name.split("/")[-1]
    content_type = mimetypes.guess_type(
        file_name)[0] or "application/octet-stream"
    response = FileResponse(application.attached_cv.open(
        "rb"), as_attachment=True, filename=file_name)
    response["Content-Type"] = content_type
    return response


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR", "TEAM_LEAD"])])
def candidate_cv_download(request, application_id):
    return application_cv_download(request, application_id)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def email_template_list_create_view(request):
    if request.method == "GET":
        templates = EmailTemplate.objects.all()
        serializer = EmailTemplateSerializer(templates, many=True)
        return Response(serializer.data, status=200)

    serializer = EmailTemplateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    template = serializer.save(created_by=request.user)
    return Response(EmailTemplateSerializer(template).data, status=201)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def email_template_list_create(request):
    return email_template_list_create_view(request)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def email_template_detail_view(request, pk):
    template = get_object_or_404(EmailTemplate, id=pk)
    if request.method == "GET":
        return Response(EmailTemplateSerializer(template).data, status=200)
    if request.method in ["PUT", "PATCH"]:
        serializer = EmailTemplateSerializer(
            template, data=request.data, partial=request.method == "PATCH")
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        serializer.save()
        return Response(serializer.data, status=200)
    template.delete()
    return Response(status=204)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def email_template_detail(request, pk):
    return email_template_detail_view(request, pk)


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def preview_candidate_email_view(request):
    serializer = EmailPreviewSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    candidate = get_object_or_404(
        Candidate, id=serializer.validated_data["candidate_id"])
    template = get_object_or_404(
        EmailTemplate, id=serializer.validated_data["template_id"])
    application = Application.objects.filter(
        candidate=candidate).order_by("-created_at").first()
    context = {
        "candidate_name": candidate.candidate_name,
        "job_title": application.job_posting.job_title if application else "Role",
        "company_name": "HR-CSS",
        "email": candidate.email,
        "phone": candidate.phone_number or "",
    }
    rendered_subject = render_email_template(template.subject, context)
    rendered_body = render_email_template(template.body, context)
    return Response({"subject": rendered_subject, "body": rendered_body}, status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def preview_candidate_email(request):
    return preview_candidate_email_view(request)


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def send_candidate_email_view(request):
    serializer = SendEmailPayloadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    payload = serializer.validated_data
    template = None
    if payload.get("template_id") is not None:
        template = get_object_or_404(EmailTemplate, id=payload["template_id"])

    application_ids = payload.get("application_ids") or []
    candidate_ids = payload.get("candidate_ids") or []
    applications = []
    if application_ids:
        applications = list(Application.objects.filter(
            id__in=application_ids).select_related("candidate", "job_posting"))
    elif candidate_ids:
        applications = list(Application.objects.filter(
            candidate_id__in=candidate_ids).select_related("candidate", "job_posting"))

    if not applications and payload.get("template_id") is None:
        return Response({"error": "No matching applications found."}, status=400)

    dispatched = []
    for application in applications:
        candidate = application.candidate
        if template:
            context = {
                "candidate_name": candidate.candidate_name,
                "job_title": application.job_posting.job_title,
                "company_name": "HR-CSS",
                "email": candidate.email,
                "phone": candidate.phone_number or "",
            }
            subject = render_email_template(template.subject, context)
            body = render_email_template(template.body, context)
        else:
            subject = payload.get("subject") or ""
            body = payload.get("body") or ""

        try:
            send_mail(subject=subject, message=body, from_email=settings.DEFAULT_FROM_EMAIL,
                      recipient_list=[candidate.email], fail_silently=False)
            status = CandidateEmailLog.EmailStatus.SUCCESS
            is_sent_successfully = True
            error_message = ""
            sent_at = timezone.now()
        except Exception as exc:
            status = CandidateEmailLog.EmailStatus.FAILED
            is_sent_successfully = False
            error_message = str(exc)
            sent_at = timezone.now()

        log = CandidateEmailLog.objects.create(
            candidate=candidate,
            job_posting=application.job_posting,
            template=template,
            sent_by=request.user,
            recipient_email=candidate.email,
            subject=subject,
            body=body,
            status=status,
            is_sent_successfully=is_sent_successfully,
            error_message=error_message,
            sent_at=sent_at,
        )
        dispatched.append(CandidateEmailLogSerializer(log).data)

    return Response({"sent_count": len(dispatched), "items": dispatched}, status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def send_candidate_email(request):
    return send_candidate_email_view(request)


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def retry_failed_email_view(request):
    failed_logs = CandidateEmailLog.objects.filter(
        status=CandidateEmailLog.EmailStatus.FAILED).select_related("candidate", "job_posting", "template")
    retried = []
    for log in failed_logs:
        try:
            send_mail(subject=log.subject, message=log.body, from_email=settings.DEFAULT_FROM_EMAIL,
                      recipient_list=[log.recipient_email or log.candidate.email], fail_silently=False)
            log.status = CandidateEmailLog.EmailStatus.SUCCESS
            log.is_sent_successfully = True
            log.error_message = ""
            log.sent_at = timezone.now()
            log.save(update_fields=[
                     "status", "is_sent_successfully", "error_message", "sent_at", "updated_at"])
            retried.append(CandidateEmailLogSerializer(log).data)
        except Exception as exc:
            log.status = CandidateEmailLog.EmailStatus.FAILED
            log.is_sent_successfully = False
            log.error_message = str(exc)
            log.sent_at = timezone.now()
            log.save(update_fields=[
                     "status", "is_sent_successfully", "error_message", "sent_at", "updated_at"])
    return Response({"retried_count": len(retried), "items": retried}, status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasRole(["ADMIN", "HR"])])
def retry_failed_candidate_email(request):
    return retry_failed_email_view(request)