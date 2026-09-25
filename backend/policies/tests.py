from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from policies.models import Policy, PolicyCategory


class PolicyListQueryFilterTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="hr@example.com",
            password="StrongPass123!",
            first_name="HR",
            last_name="Manager",
            role=get_user_model().Role.HR,
        )
        self.category_one = PolicyCategory.objects.create(
            name="People Ops",
            is_active=True,
        )
        self.category_two = PolicyCategory.objects.create(
            name="Security",
            is_active=True,
        )
        self.mandatory_policy = Policy.objects.create(
            category=self.category_one,
            title="Code of Conduct",
            content="Mandatory policy",
            version="1.0",
            is_mandatory=True,
            is_active=True,
        )
        self.optional_policy = Policy.objects.create(
            category=self.category_two,
            title="Remote Working",
            content="Optional policy",
            version="1.0",
            is_mandatory=False,
            is_active=True,
        )

    def test_policy_list_exposes_category_and_filters_by_mandatory(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.get("/api/v1/policies/", {"mandatory": "true"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.mandatory_policy.id)
        self.assertEqual(response.data[0]["category"], self.category_one.id)

        optional_response = client.get(
            "/api/v1/policies/", {"mandatory": "false"})
        self.assertEqual(optional_response.status_code, 200)
        self.assertEqual(len(optional_response.data), 1)
        self.assertEqual(
            optional_response.data[0]["id"], self.optional_policy.id)
