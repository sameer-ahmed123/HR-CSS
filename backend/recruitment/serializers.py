from rest_framework import serializers

from .models import (
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


class HiringRequesSerializer(serializers.ModelSerializer):
    class Meta:
        model = HiringRequest
        fields = [
            'id',
            'request_title',
            'department',
            'headcount',
            'seniority',
            'budget',
            'reason',
            'urgency',
            'required_experience',
            'required_qualifications',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']


class HiringRequesDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = HiringRequest
        fields = "__all__"


class HiringRequestOverviewSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source='department.name', read_only=True)
    requested_by_name = serializers.CharField(
        source='requested_by.email', read_only=True)

    class Meta:
        model = HiringRequest
        fields = [
            'id',
            'request_title',
            'department_name',
            'requested_by_name',
            'headcount',
            'urgency',
            'status',
            'created_at'
        ]


class JobPostingOverviewSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source='department.name', read_only=True)
    applicant_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = JobPosting
        fields = [
            'id',
            'job_title',
            'department_name',
            'status',
            'cv_score_threshold',
            'applicant_count',
            'created_at'
        ]


class PriorityApplicationSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(
        source='candidate.candidate_name', read_only=True)
    candidate_email = serializers.CharField(
        source='candidate.email', read_only=True)
    job_title = serializers.CharField(
        source='job_posting.job_title', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id',
            'candidate_name',
            'candidate_email',
            'job_title',
            'stage',
            'ats_score',
            'is_priority',
            'created_at'
        ]


class CandidateSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = [
            'id',
            'candidate_name',
            'email',
            'phone_number',
            'location',
            'about',
            'created_at',
        ]


class ApplicationListSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(
        source='candidate.candidate_name', read_only=True)
    candidate_email = serializers.CharField(
        source='candidate.email', read_only=True)
    candidate_phone = serializers.CharField(
        source='candidate.phone_number', read_only=True, allow_null=True)
    candidate_location = serializers.CharField(
        source='candidate.location', read_only=True, allow_blank=True)
    stage_label = serializers.CharField(
        source='get_stage_display', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id',
            'candidate_name',
            'candidate_email',
            'candidate_phone',
            'candidate_location',
            'stage',
            'stage_label',
            'ats_score',
            'is_priority',
            'created_at',
        ]


class JobPostingSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source="department.name", read_only=True)
    applicant_count = serializers.IntegerField(
        source="applications.count", read_only=True)

    class Meta:
        model = JobPosting
        fields = [
            "id",
            "job_title",
            "job_description",
            "department",
            "department_name",
            "hiring_request",
            "status",
            "required_skills",
            "required_experience",
            "closing_date",
            "cv_score_threshold",
            "linkedin_post_id",
            "linkedin_post_url",
            "applicant_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "applicant_count"]

    def validate_hiring_request(self, value):
        if value and value.status != HiringRequest.RequestStatus.APPROVED:
            raise serializers.ValidationError(
                "Cannot link a job posting to an unapproved hiring request."
            )
        return value


class CVScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVScore
        fields = [
            "id",
            "overall_score",
            "skills_score",
            "experience_score",
            "education_score",
            "breakdown_notes",
            "scored_at",
        ]


class CVScoreBreakdownSerializer(CVScoreSerializer):
    class Meta(CVScoreSerializer.Meta):
        pass


class ApplicationStageHistorySerializer(serializers.ModelSerializer):
    changed_by_email = serializers.CharField(
        source='changed_by.email', read_only=True)

    class Meta:
        model = ApplicationStageHistory
        fields = [
            "id",
            "old_stage",
            "new_stage",
            "changed_by",
            "changed_by_email",
            "timestamp",
        ]


class CandidateNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.email', read_only=True)

    class Meta:
        model = CandidateNote
        fields = [
            "id",
            "author",
            "author_name",
            "text",
            "created_at",
        ]


class ApplicationDetailSerializer(serializers.ModelSerializer):
    candidate = CandidateSummarySerializer(read_only=True)
    job_posting = JobPostingSerializer(read_only=True)
    stage_label = serializers.CharField(
        source='get_stage_display', read_only=True)
    cv_score = CVScoreSerializer(read_only=True)
    stage_history = ApplicationStageHistorySerializer(
        many=True, read_only=True)
    notes = CandidateNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = [
            'id',
            'candidate',
            'job_posting',
            'attached_cv',
            'stage',
            'stage_label',
            'ats_score',
            'score_reasons',
            'is_priority',
            'cv_score',
            'stage_history',
            'notes',
            'created_at',
            'updated_at',
        ]


class PublicJobPostingSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source="department.name", read_only=True)

    class Meta:
        model = JobPosting
        fields = [
            "id",
            "job_title",
            "job_description",
            "department_name",
            "required_skills",
            "required_experience",
            "closing_date",
            "cv_score_threshold",
            "created_at",
        ]


class JobApplicationSubmitSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=500)
    email = serializers.EmailField()
    phone = serializers.CharField(
        max_length=50, required=False, allow_blank=True)
    address = serializers.CharField(
        max_length=500, required=False, allow_blank=True)
    cover_letter = serializers.CharField(
        required=False, allow_blank=True, trim_whitespace=False)
    links = serializers.JSONField(required=False, allow_null=True)
    cv = serializers.FileField(required=True, allow_empty_file=False)

    def validate_links(self, value):
        if value in (None, ""):
            return []

        if isinstance(value, str):
            import json
            try:
                parsed = json.loads(value)
            except (TypeError, ValueError):
                return []
            value = parsed

        if not isinstance(value, list):
            return []

        normalized_links = []
        for item in value:
            if isinstance(item, str):
                url = item.strip()
                if url:
                    normalized_links.append({"label": "Link", "url": url})
                continue

            if isinstance(item, dict):
                url = str(item.get("url", "") or "").strip()
                label = str(item.get("label", "") or "").strip() or "Link"
                if url:
                    normalized_links.append({"label": label, "url": url})

        return normalized_links


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = [
            'id',
            'name',
            'template_type',
            'subject',
            'body',
            'is_active',
            'created_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class CandidateEmailLogSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(
        source='candidate.candidate_name', read_only=True)
    job_title = serializers.CharField(
        source='job_posting.job_title', read_only=True)

    class Meta:
        model = CandidateEmailLog
        fields = [
            'id',
            'candidate',
            'candidate_name',
            'job_posting',
            'job_title',
            'template',
            'recipient_email',
            'subject',
            'body',
            'status',
            'is_sent_successfully',
            'error_message',
            'sent_at',
            'created_at',
        ]


class EmailPreviewSerializer(serializers.Serializer):
    candidate_id = serializers.IntegerField()
    template_id = serializers.IntegerField()


class SendEmailPayloadSerializer(serializers.Serializer):
    template_id = serializers.IntegerField(required=False, allow_null=True)
    candidate_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False)
    application_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False)
    subject = serializers.CharField(required=False, allow_blank=True)
    body = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        candidate_ids = attrs.get('candidate_ids') or []
        application_ids = attrs.get('application_ids') or []
        if not candidate_ids and not application_ids and not attrs.get('template_id'):
            raise serializers.ValidationError(
                'Provide candidate_ids or application_ids, and a template_id or explicit subject/body.')
        return attrs


class BulkStageUpdateSerializer(serializers.Serializer):
    application_ids = serializers.ListField(child=serializers.IntegerField())
    new_stage = serializers.ChoiceField(choices=Application.Stage.choices)


class CandidatePipelineListSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(
        source='candidate.candidate_name', read_only=True)
    candidate_email = serializers.CharField(
        source='candidate.email', read_only=True)
    stage_label = serializers.CharField(
        source='get_stage_display', read_only=True)
    score_breakdown = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            'id',
            'candidate_name',
            'candidate_email',
            'stage',
            'stage_label',
            'ats_score',
            'is_priority',
            'score_breakdown',
            'created_at',
        ]

    def get_score_breakdown(self, obj):
        cv_score = getattr(obj, 'cv_score', None)
        if not cv_score:
            return None
        return CVScoreSerializer(cv_score).data

# ==========================================
# DASHBOARD OVERVIEW SERIALIZER
# ==========================================


class RecruitmentOverviewSerializer(serializers.Serializer):
    # Summary Metrics
    total_open_jobs = serializers.IntegerField()
    pending_hiring_requests_count = serializers.IntegerField()
    new_applications_this_week = serializers.IntegerField()
    emails_sent_this_week = serializers.IntegerField()

    # Detailed Collections / Lists
    open_jobs = JobPostingOverviewSerializer(many=True)
    pending_hiring_requests = HiringRequestOverviewSerializer(many=True)
    priority_candidates = PriorityApplicationSerializer(many=True)
    pipeline_funnel = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Count of applications per hiring stage"
    )
