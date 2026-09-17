from rest_framework import serializers
from .models import HiringRequest, JobPosting, Candidate, Application, CandidateEmailLog


class HiringRequesSerializer(serializers.ModelSerializer):
    class Meta:
        model = HiringRequest
        fields = [
            'id',
            'request_title',
            'department',
            'headcount',
            'urgency',
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
