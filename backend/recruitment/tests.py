from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from authentication.models import CustomUser
from organization.models import Department
from recruitment.models import Application, Candidate, CandidateEmailLog, HiringRequest, JobPosting
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

    def test_public_job_list_and_apply_flow(self):
        job = JobPosting.objects.create(
            department=self.department,
            job_title="Python Engineer",
            job_description="Build APIs for the platform team.",
            required_skills="Python, Django",
            required_experience="3+ years",
            status=JobPosting.JobStatus.PUBLISHED,
        )

        list_response = self.client.get(reverse("public_job_list"))
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.json()[
                         0]["job_title"], "Python Engineer")

        detail_response = self.client.get(
            reverse("public_job_detail", kwargs={"job_id": job.id}))
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()[
                         "job_title"], "Python Engineer")

        first_payload = {
            "full_name": "Jane Candidate",
            "email": "jane@example.com",
            "phone": "123456789",
            "cv": SimpleUploadedFile("cv.pdf", b"pdf-content", content_type="application/pdf"),
        }
        apply_response = self.client.post(
            reverse("public_job_apply", kwargs={"job_id": job.id}),
            first_payload,
            format="multipart",
        )
        self.assertEqual(apply_response.status_code, 201)
        self.assertTrue(Candidate.objects.filter(
            email="jane@example.com").exists())
        self.assertTrue(Application.objects.filter(job_posting=job).exists())
        self.assertTrue(CandidateEmailLog.objects.filter(
            candidate__email="jane@example.com").exists())

        duplicate_payload = {
            "full_name": "Jane Candidate",
            "email": "jane@example.com",
            "phone": "123456789",
            "cv": SimpleUploadedFile("cv-duplicate.pdf", b"pdf-content", content_type="application/pdf"),
        }
        duplicate_response = self.client.post(
            reverse("public_job_apply", kwargs={"job_id": job.id}),
            duplicate_payload,
            format="multipart",
        )
        self.assertEqual(duplicate_response.status_code, 400)
        self.assertIn("already applied",
                      duplicate_response.json()["error"].lower())

    def test_public_job_apply_accepts_named_links(self):
        job = JobPosting.objects.create(
            department=self.department,
            job_title="Product Designer",
            job_description="Design product experiences.",
            required_skills="Figma, UX",
            required_experience="2+ years",
            status=JobPosting.JobStatus.PUBLISHED,
        )

        payload = {
            "full_name": "Design Candidate",
            "email": "design@example.com",
            "phone": "987654321",
            "links": '[{"label":"GitHub","url":"https://github.com/design"},{"label":"Portfolio","url":"https://example.com"}]',
            "cv": SimpleUploadedFile("cv.pdf", b"pdf-content", content_type="application/pdf"),
        }

        response = self.client.post(
            reverse("public_job_apply", kwargs={"job_id": job.id}),
            payload,
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
        candidate = Candidate.objects.get(email="design@example.com")
        self.assertIn("GitHub", candidate.candidate_skills)
        self.assertIn("https://github.com/design", candidate.candidate_skills)

    def test_job_posting_application_list_and_detail_endpoints(self):
        self.hiring_request.status = HiringRequest.RequestStatus.APPROVED
        self.hiring_request.save()

        job = JobPosting.objects.create(
            department=self.department,
            hiring_request=self.hiring_request,
            job_title="Senior Backend Engineer",
            job_description="Build backend applications.",
            required_skills="Python, Django",
            required_experience="5+ years",
            status=JobPosting.JobStatus.PUBLISHED,
        )

        candidate = Candidate.objects.create(
            candidate_name="Alice Candidate",
            email="alice@example.com",
            phone_number="111",
            location="Lagos",
            about="Experienced backend engineer.",
        )

        application = Application.objects.create(
            candidate=candidate,
            job_posting=job,
            attached_cv=SimpleUploadedFile(
                "alice.pdf", b"cv", content_type="application/pdf"),
            stage=Application.Stage.NEW,
            ats_score=82,
            is_priority=True,
        )

        api_client = APIClient()
        api_client.force_authenticate(user=self.approver)

        list_response = api_client.get(
            reverse("job-posting-applications", kwargs={"pk": job.id})
        )
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()), 1)
        self.assertEqual(list_response.json()[
                         0]["candidate_name"], "Alice Candidate")

        detail_response = api_client.get(
            reverse(
                "job-posting-application-detail",
                kwargs={"pk": job.id, "application_id": application.id},
            )
        )
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()[
                         "candidate"]["email"], "alice@example.com")
        self.assertEqual(detail_response.json()["job_posting"]["id"], job.id)
