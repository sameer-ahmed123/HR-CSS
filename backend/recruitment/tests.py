from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory, force_authenticate

from authentication.models import CustomUser
from organization.models import Department
from recruitment.models import HiringRequest, JobPosting
from recruitment.views import hiring_request_hr_action


class HiringRequestApprovalJobPostingTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.department = Department.objects.create(
            name="Engineering",
            code="ENG",
            description="Engineering department",
        )
        self.approver = CustomUser.objects.create_user(
            email="hr@example.com",
            password="StrongPass123!",
            first_name="HR",
            last_name="Approver",
            role=CustomUser.Role.HR,
        )
        self.requester = CustomUser.objects.create_user(
            email="lead@example.com",
            password="StrongPass123!",
            first_name="Team",
            last_name="Lead",
            role=CustomUser.Role.TEAM_LEAD,
            department=self.department,
        )
        self.hiring_request = HiringRequest.objects.create(
            request_title="Senior Backend Engineer",
            department=self.department,
            requested_by=self.requester,
            headcount=2,
            seniority="Senior",
            budget="120000",
            reason="Need more backend capacity for the platform team.",
            urgency=HiringRequest.UrgencyLevel.HIGH,
            required_experience="5+ years in Python and Django",
            required_qualifications="Python, Django, PostgreSQL, system design",
            status=HiringRequest.RequestStatus.PENDING,
        )

    def test_approve_hiring_request_creates_job_posting_when_requested(self):
        url = reverse("hiring_request_staus", kwargs={
                      "pk": self.hiring_request.pk})
        request = self.factory.patch(
            url,
            {"status": HiringRequest.RequestStatus.APPROVED,
                "create_job_posting": True},
            format="json",
        )
        force_authenticate(request, user=self.approver)

        response = hiring_request_hr_action(request, self.hiring_request.pk)

        self.assertEqual(response.status_code, 200)
        self.hiring_request.refresh_from_db()
        self.assertEqual(self.hiring_request.status,
                         HiringRequest.RequestStatus.APPROVED)

        job_posting = JobPosting.objects.get(
            hiring_request=self.hiring_request)
        self.assertEqual(job_posting.department, self.department)
        self.assertEqual(job_posting.job_title,
                         self.hiring_request.request_title)
        self.assertEqual(job_posting.status, JobPosting.JobStatus.DRAFT)
        self.assertIn("Python", job_posting.required_skills)
