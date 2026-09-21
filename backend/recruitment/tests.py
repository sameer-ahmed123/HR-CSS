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

    def test_team_lead_can_edit_draft_job_posting_in_their_department(self):
        team_lead = CustomUser.objects.create_user(
            email="eng-team-lead@example.com",
            password="StrongPass123!",
            first_name="Eng",
            last_name="Lead",
            role=CustomUser.Role.TEAM_LEAD,
            department=self.department,
        )
        job = JobPosting.objects.create(
            department=self.department,
            job_title="Python Engineer",
            job_description="Build APIs for the platform team.",
            required_skills="Python, Django",
            required_experience="3+ years",
            status=JobPosting.JobStatus.DRAFT,
        )

        client = APIClient()
        client.force_authenticate(user=team_lead)

        response = client.patch(
            reverse("job-posting-detail", kwargs={"pk": job.id}),
            {
                "job_description": "Build backend APIs and improve platform reliability.",
                "required_experience": "5+ years of Python and Django experience",
                "required_skills": "Python, Django, PostgreSQL, system design",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        job.refresh_from_db()
        self.assertEqual(job.job_description,
                         "Build backend APIs and improve platform reliability.")
        self.assertEqual(
            job.required_experience,
            "5+ years of Python and Django experience",
        )
        self.assertIn("PostgreSQL", job.required_skills)

    def test_team_lead_cannot_edit_published_job_posting(self):
        team_lead = CustomUser.objects.create_user(
            email="eng-team-lead-published@example.com",
            password="StrongPass123!",
            first_name="Eng",
            last_name="Lead",
            role=CustomUser.Role.TEAM_LEAD,
            department=self.department,
        )
        job = JobPosting.objects.create(
            department=self.department,
            job_title="Python Engineer",
            job_description="Build APIs for the platform team.",
            required_skills="Python, Django",
            required_experience="3+ years",
            status=JobPosting.JobStatus.PUBLISHED,
        )

        client = APIClient()
        client.force_authenticate(user=team_lead)

        response = client.patch(
            reverse("job-posting-detail", kwargs={"pk": job.id}),
            {
                "job_description": "This should not be allowed.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        job.refresh_from_db()
        self.assertNotEqual(job.job_description, "This should not be allowed.")

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


class RecruitmentATSAndPipelineTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(
            name="Platform",
            code="PLAT",
            description="Platform engineering",
        )
        self.hr = CustomUser.objects.create_user(
            email="ats.hr@example.com",
            password="StrongPass123!",
            first_name="ATS",
            last_name="HR",
            role=CustomUser.Role.HR,
            department=self.department,
        )
        self.job = JobPosting.objects.create(
            department=self.department,
            job_title="Senior Python Engineer",
            job_description="Build backend systems and APIs.",
            required_skills="Python, Django, PostgreSQL",
            required_experience="5+ years",
            cv_score_threshold=70,
            status=JobPosting.JobStatus.PUBLISHED,
        )
        self.candidate = Candidate.objects.create(
            candidate_name="Candidate Alpha",
            email="alpha@example.com",
            phone_number="000111",
            candidate_skills="Python, Django, PostgreSQL, Redis",
            location="Lagos",
            about="5 years of Python and Django engineering with a Bachelor's degree.",
        )
        self.application = Application.objects.create(
            candidate=self.candidate,
            job_posting=self.job,
            attached_cv=SimpleUploadedFile(
                "alpha.pdf", b"pdf", content_type="application/pdf"
            ),
            stage=Application.Stage.NEW,
            ats_score=0,
        )

    def test_run_cv_scoring_updates_application_score_and_priority(self):
        client = APIClient()
        client.force_authenticate(user=self.hr)

        response = client.post(
            reverse("run_cv_scoring_view", kwargs={
                    "application_id": self.application.id})
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreater(payload["overall_score"], 0)
        self.assertIn("skills_score", payload)
        self.assertIn("breakdown_notes", payload)

        self.application.refresh_from_db()
        self.assertGreaterEqual(self.application.ats_score, 0)
        self.assertTrue(
            self.application.is_priority or self.application.ats_score >= 0)

    def test_pipeline_stage_and_email_template_preview_work(self):
        client = APIClient()
        client.force_authenticate(user=self.hr)

        stage_response = client.patch(
            reverse("update_application_stage_view", kwargs={
                    "application_id": self.application.id}),
            {"new_stage": "REVIEWED"},
            format="json",
        )
        self.assertEqual(stage_response.status_code, 200)
        self.assertEqual(stage_response.json()["stage"], "REVIEWED")

        template_response = client.post(
            reverse("email_template_list_create_view"),
            {
                "name": "Interview Invite",
                "template_type": "INTERVIEW_INVITATION",
                "subject": "Interview for {{candidate_name}}",
                "body": "Hi {{candidate_name}}, we would like to interview you for {{job_title}}.",
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(template_response.status_code, 201)
        template_id = template_response.json()["id"]

        preview = client.post(
            reverse("preview_candidate_email_view"),
            {"candidate_id": self.candidate.id, "template_id": template_id},
            format="json",
        )
        self.assertEqual(preview.status_code, 200)
        self.assertIn("Candidate Alpha", preview.json()["subject"])
        self.assertIn("Senior Python Engineer", preview.json()["body"])

    def test_email_suite_alias_contract(self):
        client = APIClient()
        client.force_authenticate(user=self.hr)

        template_response = client.post(
            reverse("email_template_list_create"),
            {
                "name": "Welcome Note",
                "template_type": "CUSTOM",
                "subject": "Hi {{candidate_name}}",
                "body": "Hello {{candidate_name}} for {{job_title}}.",
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(template_response.status_code, 201)

        preview = client.post(
            reverse("preview_candidate_email"),
            {"candidate_id": self.candidate.id, "template_id": template_response.json()[
                "id"]},
            format="json",
        )
        self.assertEqual(preview.status_code, 200)
        self.assertIn("Candidate Alpha", preview.json()["subject"])

        send_response = client.post(
            reverse("send_candidate_email"),
            {"template_id": template_response.json()["id"], "candidate_ids": [
                self.candidate.id]},
            format="json",
        )
        self.assertEqual(send_response.status_code, 200)
        self.assertGreaterEqual(send_response.json()["sent_count"], 1)

    def test_pipeline_alias_and_cv_download_contract(self):
        client = APIClient()
        client.force_authenticate(user=self.hr)

        list_response = client.get(
            reverse("candidate_pipeline_list", kwargs={"job_id": self.job.id})
        )
        self.assertEqual(list_response.status_code, 200)
        self.assertGreater(len(list_response.json()), 0)

        cv_response = client.get(
            reverse("application_cv_download", kwargs={
                    "application_id": self.application.id})
        )
        self.assertEqual(cv_response.status_code, 200)
        self.assertIn("application/pdf", cv_response["Content-Type"])
