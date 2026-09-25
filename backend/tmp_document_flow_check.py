from documents.models import DocumentRequest, DocumentTemplate, DocumentTypeConfig
from organization.models import Department
from rest_framework.test import APIClient
from django.test import override_settings
from django.contrib.auth import get_user_model
import django
import os
from uuid import uuid4

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()


User = get_user_model()

dep = Department.objects.create(
    name='Engineering',
    code='ENG-' + uuid4().hex[:6].upper(),
    description='Engineering'
)

hr = User.objects.create_user(
    email='hr-' + uuid4().hex[:8] + '@company.com',
    password='testpass123',
    first_name='HR',
    last_name='User',
    role='HR',
    department=dep,
)

employee = User.objects.create_user(
    email='emp-' + uuid4().hex[:8] + '@company.com',
    password='testpass123',
    first_name='Jane',
    last_name='Doe',
    role='EMPLOYEE',
    department=dep,
)

code = 'EXP_' + uuid4().hex[:8].upper()
doc_type = DocumentTypeConfig.objects.create(
    code=code,
    name='Experience Letter',
    description='Test',
    turnaround_days=3,
    is_active=True,
)

DocumentTemplate.objects.create(
    document_type=doc_type,
    title='Experience Letter',
    body_content='Dear {{employee_name}},<br>Department: {{department}}<br>Purpose: {{purpose}}<br>Ref: {{reference_number}}',
    include_letterhead=True,
    footer_text='Footer',
)

doc_request = DocumentRequest.objects.create(
    requested_by=employee,
    document_type=doc_type,
    purpose='Employment verification',
    needed_by='2026-12-31',
    status=DocumentRequest.RequestChoice.PENDING,
)

client = APIClient()
client.force_authenticate(user=hr)

with override_settings(ALLOWED_HOSTS=['testserver']):
    preview_resp = client.get(
        f'/api/v1/documents/request/{doc_request.id}/preview/')
    print('preview_status', preview_resp.status_code)
    print('preview_has_html', 'html' in preview_resp.json())

    issue_resp = client.post(
        f'/api/v1/documents/request/{doc_request.id}/issue/',
        {},
        format='json',
    )
    print('issue_status', issue_resp.status_code)
    print('issue_status_value', issue_resp.json().get('status'))
    print('generated_file_present', bool(
        issue_resp.json().get('generated_file')))
    print('assigned_hr_set', bool(issue_resp.json().get('assigned_hr')))
