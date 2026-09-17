from django.db import models
from django.conf import UserSettingsHolder, settings
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
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    reason = models.TextField()
    urgency = models.CharField(max_length=20, choices=UrgencyLevel.choices, default=UrgencyLevel.MEDIUM)
    required_experience = models.CharField(max_length=250)
    required_qualifications = models.TextField(max_length=2500)
    status = models.CharField(max_length=20, choices=RequestStatus.choices, default=RequestStatus.PENDING)
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
    cv_score_threshold = models.IntegerField(default=70)  # ATS score benchmark
    status = models.CharField(max_length=20, choices=JobStatus.choices, default=JobStatus.DRAFT)
    
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
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.NEW)
    
    ats_score = models.IntegerField(default=0)
    score_reasons = models.JSONField(default=dict, blank=True)  # Stores breakdown of ATS evaluation
    is_priority = models.BooleanField(default=False)

    class Meta:
        unique_together = ['candidate', 'job_posting']

    def __str__(self):
        return f"{self.candidate.candidate_name} - {self.job_posting.job_title}"


class CandidateEmailLog(TimeStampedModel):
    candidate = models.ForeignKey(
        Candidate, 
        on_delete=models.CASCADE, 
        related_name='email_logs'
    )
    job_posting = models.ForeignKey(
        JobPosting, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    is_sent_successfully = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Email to {self.candidate.email} on {self.created_at.strftime('%Y-%m-%d')}"