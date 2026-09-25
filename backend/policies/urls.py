from django.urls import path

from policies.views import (
    archive_policy_view,
    create_policy_version_view,
    my_acknowledgments,
    pending_acknowledgements,
    policy_acknowledge_view,
    policy_category_list_create_view,
    policy_compliance_report_view,
    policy_detail_view,
    policy_list_create_view,
    send_policy_reminder_view,
)

urlpatterns = [
    # Policy list + create
    path("", policy_list_create_view, name="policies"),

    # Policy detail and delete/update
    path("<int:pk>/", policy_detail_view, name="policy_detail"),

    # Policy acknowledgements and user-specific policy views
    path("<int:pk>/acknowledge/", policy_acknowledge_view,
         name="policy_acknowledge"),
    path("my-acknowledgments/", my_acknowledgments, name="my_acknowledgments"),
    path("pending-acknowledgements/", pending_acknowledgements,
         name="pending_acknowledgements"),

    # Policy categories
    path("categories/", policy_category_list_create_view, name="policy_category"),

    # Versioning, archiving, compliance, reminder workflow
    path("<int:pk>/create-version/", create_policy_version_view,
         name="policy_create_version"),
    path("<int:pk>/archive/", archive_policy_view, name="policy_archive"),
    path("<int:pk>/compliance-report/", policy_compliance_report_view,
         name="policy_compliance_report"),
    path("<int:pk>/send-reminder/", send_policy_reminder_view,
         name="policy_send_reminder"),
]
