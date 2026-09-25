from django.db import models
from django.conf import settings


class DocumentTypeConfig(models.Model):
    class DocumentCode(models.TextChoices):
        EXPERIENCE_LETTER = 'EXP_LET', 'Experience Letter'
        APPOINTMENT_LETTER = 'APT_LET', 'Appointment Letter'
        INCOME_TAX_CERTIFICATE = 'ITC', 'Income Tax Certificate'
        NOC = 'NOC', 'NOC File'
        SALARY_CERTIFICATE = 'SC', 'Salary Certificate'

    code = models.CharField(
        max_length=50,
        choices=DocumentCode.choices,
        unique=True
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    turnaround_days = models.PositiveIntegerField(
        default=3,
        help_text="Expected SLA in business days to fulfill this request."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="If False, employees cannot select this type when making new requests."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class DocumentTemplate(models.Model):
    document_type = models.OneToOneField(
        DocumentTypeConfig,
        on_delete=models.CASCADE,
        related_name="template"
    )
    title = models.CharField(max_length=255)
    body_content = models.TextField(
        help_text="HTML or Plain text template. Use placeholders like {{employee_name}}, {{designation}}, {{monthly_salary}}, {{joining_date}}."
    )
    include_letterhead = models.BooleanField(default=True)
    letterhead_image = models.ImageField(
        upload_to="letterheads/", blank=True, null=True)
    footer_text = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Template for {self.document_type.name}"


class DocumentRequest(models.Model):
    class RequestChoice(models.TextChoices):
        PENDING = "PENDING", "pending"
        IN_PROGRESS = "IN_PROGRESS", "in progress"
        READY = "READY", "ready"
        DELIVERED = "DELIVERED", "delivered"
        REJECTED = "REJECTED", "rejected"
        CANCELLED = "CANCELLED", "cancelled"

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="document_request")
    document_type = models.ForeignKey(
        DocumentTypeConfig, on_delete=models.CASCADE, related_name="document_request")
    purpose = models.TextField(max_length=2500)
    needed_by = models.DateField()
    expected_completion_date = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=250, choices=RequestChoice.choices, default=RequestChoice.PENDING)
    rejection_reason = models.CharField(max_length=500, null=True, blank=True)
    assigned_hr = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="assigned_document_requests")
    reference_number = models.CharField(
        max_length=80, blank=True, null=True, unique=True,
        help_text="Persistent unique reference number for the issued document."
    )
    file_version = models.PositiveIntegerField(default=1)
    manual_upload = models.BooleanField(default=False)
    generated_file = models.FileField(
        null=True, blank=True, upload_to="generated_documents/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.requested_by.email} requested {self.document_type.name} by {self.needed_by}"
