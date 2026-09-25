from django.contrib.auth import get_user_model
from django.test import TestCase

from documents.models import DocumentRequest, DocumentTemplate, DocumentTypeConfig
from documents.services import get_document_context
from organization.models import Department


class DocumentLetterGenerationTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(
            name="Engineering",
            code="ENG",
            description="Engineering department",
        )
        self.user = get_user_model().objects.create_user(
            email="alice@example.com",
            password="StrongPass123!",
            first_name="Alice",
            last_name="Brown",
            role=get_user_model().Role.EMPLOYEE,
            department=self.department,
        )
        self.user.current_designation = "Senior Developer"
        self.user.salary = 75000

        self.doc_type = DocumentTypeConfig.objects.create(
            code="EXP_LET",
            name="Experience Letter",
            description="Experience letter",
        )
        self.template = DocumentTemplate.objects.create(
            document_type=self.doc_type,
            title="Experience Letter",
            body_content="Dear {{employee_name}},\nDepartment: {{department}}\nDesignation: {{designation}}\nSalary: {{salary}}\nReference: {{reference_number}}",
        )

    def test_context_includes_salary_and_persistent_reference_number(self):
        document_request = DocumentRequest.objects.create(
            requested_by=self.user,
            document_type=self.doc_type,
            purpose="Employment verification",
            needed_by="2026-10-15",
        )

        context = get_document_context(document_request)

        self.assertEqual(context["{{employee_name}}"], "Alice Brown")
        self.assertEqual(context["{{department}}"], "Engineering")
        self.assertEqual(context["{{designation}}"], "Senior Developer")
        self.assertTrue(context["{{reference_number}}"].startswith("DOC-"))
        self.assertIn("Rs.", context["{{salary}}"])
        self.assertIn("{{reference_number}}", self.template.body_content)
