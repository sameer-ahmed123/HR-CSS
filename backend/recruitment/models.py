from django.conf import settings
from django.db import models

from common.models import TimeStampedModel


class HiringRequest(TimeStampedModel):

    class RequestStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PENDING = 'PENDING', 'Pending HR Approval'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        MORE_INFO = 'MORE_INFO', 'More Info Requested'

    class UrgencyLevel(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        URGENT = 'URGENT', 'Urgent'

    request_title = models.CharField(max_length=500)
    department = models.ForeignKey(
        'organization.Department',
        on_delete=models.CASCADE,
        related_name='hiring_requests'
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_hiring_requests'
    )
    headcount = models.PositiveIntegerField(default=1)
    seniority = models.CharField(max_length=100)
    budget = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    reason = models.TextField()
    urgency = models.CharField(
        max_length=20, choices=UrgencyLevel.choices, default=UrgencyLevel.MEDIUM)
    required_experience = models.CharField(max_length=250)
    required_qualifications = models.TextField(max_length=2500)
    status = models.CharField(
        max_length=20, choices=RequestStatus.choices, default=RequestStatus.PENDING)
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.request_title} ({self.department.name})"


class JobPosting(TimeStampedModel):
    class JobStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PUBLISHED = 'PUBLISHED', 'Published'
        CLOSED = 'CLOSED', 'Closed'

    hiring_request = models.ForeignKey(
        HiringRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_postings'
    )
    department = models.ForeignKey(
        'organization.Department',
        on_delete=models.CASCADE,
        related_name='job_postings'
    )
    job_title = models.CharField(max_length=500)
    job_description = models.TextField(max_length=5000)
    required_skills = models.CharField(max_length=1500)
    required_experience = models.CharField(max_length=250)
    closing_date = models.DateField(null=True, blank=True)
    cv_score_threshold = models.IntegerField(default=70)
    status = models.CharField(
        max_length=20, choices=JobStatus.choices, default=JobStatus.DRAFT)

    linkedin_post_id = models.CharField(max_length=255, blank=True, null=True)
    linkedin_post_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.job_title} - {self.status}"


class Candidate(TimeStampedModel):
    candidate_name = models.CharField(max_length=500)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    candidate_skills = models.CharField(max_length=1500, blank=True)
    location = models.CharField(max_length=500, blank=True)
    about = models.TextField(max_length=2500, blank=True)

    def __str__(self):
        return f"{self.candidate_name} ({self.email})"


class Application(TimeStampedModel):
    class Stage(models.TextChoices):
        NEW = 'NEW', 'New'
        REVIEWED = 'REVIEWED', 'Reviewed'
        SHORTLISTED = 'SHORTLISTED', 'Shortlisted'
        TEST_SENT = 'TEST_SENT', 'Test Sent'
        INTERVIEW = 'INTERVIEW', 'Interview'
        OFFER = 'OFFER', 'Offer'
        HIRED = 'HIRED', 'Hired'
        REJECTED = 'REJECTED', 'Rejected'

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    job_posting = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    attached_cv = models.FileField(upload_to='candidates/cvs/')
    stage = models.CharField(
        max_length=20, choices=Stage.choices, default=Stage.NEW)
    ats_score = models.IntegerField(default=0)
    score_reasons = models.JSONField(default=dict, blank=True)
    is_priority = models.BooleanField(default=False)

    class Meta:
        unique_together = ['candidate', 'job_posting']

    def __str__(self):
        return f"{self.candidate.candidate_name} - {self.job_posting.job_title}"


class CVScore(TimeStampedModel):
    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name='cv_score'
    )
    overall_score = models.PositiveSmallIntegerField(default=0)
    skills_score = models.PositiveSmallIntegerField(default=0)
    experience_score = models.PositiveSmallIntegerField(default=0)
    education_score = models.PositiveSmallIntegerField(default=0)
    breakdown_notes = models.TextField(blank=True, default='')
    scored_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CV score for {self.application_id}: {self.overall_score}"


class ApplicationStageHistory(TimeStampedModel):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='stage_history'
    )
    old_stage = models.CharField(
        max_length=20,
        choices=Application.Stage.choices,
        null=True,
        blank=True,
    )
    new_stage = models.CharField(
        max_length=20,
        choices=Application.Stage.choices,
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='application_stage_changes'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.application_id}: {self.old_stage or 'None'} -> {self.new_stage}"


class CandidateNote(TimeStampedModel):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='candidate_notes'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note on {self.application_id} by {self.author}"


class EmailTemplate(TimeStampedModel):
    class TemplateType(models.TextChoices):
        REJECTION = 'REJECTION', 'Rejection'
        SHORTLISTED = 'SHORTLISTED', 'Shortlisted'
        TEST_INVITATION = 'TEST_INVITATION', 'Test Invitation'
        INTERVIEW_INVITATION = 'INTERVIEW_INVITATION', 'Interview Invitation'
        OFFER = 'OFFER', 'Offer'
        HIRED = 'HIRED', 'Hired'
        CUSTOM = 'CUSTOM', 'Custom'

    name = models.CharField(max_length=200)
    template_type = models.CharField(
        max_length=30, choices=TemplateType.choices, default=TemplateType.CUSTOM)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_email_templates'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class CandidateEmailLog(TimeStampedModel):
    class EmailStatus(models.TextChoices):
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='email_logs'
    )
    job_posting = models.ForeignKey(
        JobPosting,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs'
    )
    template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs'
    )
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_candidate_emails'
    )
    recipient_email = models.EmailField(max_length=254, blank=True, default='')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(
        max_length=20, choices=EmailStatus.choices, default=EmailStatus.SUCCESS)
    is_sent_successfully = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Email to {self.recipient_email or self.candidate.email} on {self.created_at.strftime('%Y-%m-%d')}"
