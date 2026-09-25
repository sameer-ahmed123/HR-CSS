from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from policies.models import Policy, PolicyAcknowledgement, PolicyCategory, PolicyVersionHistory
from policies.serializers import (
    PolicyAcknowledgementSerializer,
    PolicyCategorySerializer,
    PolicyComplianceReportSerializer,
    PolicyDetailSerializer,
    PolicyListSerializer,
    PolicyVersionHistorySerializer,
)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def policy_category_list_create_view(request):
    if request.method == "GET":
        policy_category_qs = PolicyCategory.objects.filter(is_active=True).annotate(
            total_policies=Count("policies")
        )
        serializer = PolicyCategorySerializer(policy_category_qs, many=True)
        return Response(serializer.data, status=200)

    if request.method == "POST":
        if request.user.role not in ["ADMIN", "HR"]:
            return Response(
                {"error": "Only Admin or HR can manage policy categories."},
                status=403,
            )

        serializer = PolicyCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def policy_list_create_view(request):
    if request.method == "GET":
        if request.user.role not in ["ADMIN", "HR"]:
            policy_qs = Policy.objects.select_related(
                "category").filter(is_active=True)
        else:
            policy_qs = Policy.objects.select_related("category").all()

        category_param = request.query_params.get("category")
        search_param = request.query_params.get("search")
        mandatory_param = request.query_params.get("mandatory")

        if category_param:
            policy_qs = policy_qs.filter(category_id=category_param)
        if search_param:
            policy_qs = policy_qs.filter(
                Q(title__icontains=search_param) | Q(
                    content__icontains=search_param)
            )
        if mandatory_param is not None:
            normalized = str(mandatory_param).strip().lower()
            if normalized in ["true", "1", "t", "yes", "y"]:
                policy_qs = policy_qs.filter(is_mandatory=True)
            elif normalized in ["false", "0", "f", "no", "n"]:
                policy_qs = policy_qs.filter(is_mandatory=False)

        serializer = PolicyListSerializer(
            policy_qs, many=True, context={"request": request})
        return Response(serializer.data, status=200)

    if request.method == "POST":
        if request.user.role not in ["ADMIN", "HR"]:
            return Response(
                {"error": "Only Admin or HR can create policies."},
                status=403,
            )

        serializer = PolicyDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def policy_detail_view(request, pk):
    policy = get_object_or_404(
        Policy.objects.select_related("category"), id=pk)

    if request.method == "GET":
        serializer = PolicyDetailSerializer(policy)
        return Response(serializer.data, status=200)

    if request.method in ["PUT", "PATCH"]:
        if request.user.role not in ["ADMIN", "HR"]:
            return Response(
                {"error": "Only Admin or HR can update policies."},
                status=403,
            )

        serializer = PolicyDetailSerializer(
            policy,
            data=request.data,
            partial=(request.method == "PATCH"),
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    if request.method == "DELETE":
        if request.user.role not in ["ADMIN", "HR"]:
            return Response(
                {"error": "Only Admin or HR can delete policies."},
                status=403,
            )
        policy.delete()
        return Response(status=204)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def policy_acknowledge_view(request, pk):
    policy = get_object_or_404(Policy, id=pk)

    if request.user.role not in ["ADMIN", "HR"] and request.user.role != "EMPLOYEE":
        return Response({"detail": "You are not allowed to acknowledge this policy."}, status=403)

    if PolicyAcknowledgement.objects.filter(
        user=request.user,
        policy=policy,
        policy_version=policy.version,
    ).exists():
        return Response({"detail": "Policy already acknowledged for the current version."}, status=400)

    serializer = PolicyAcknowledgementSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(
            policy=policy,
            user=request.user,
            policy_version=policy.version,
        )
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_acknowledgments(request):
    my_ack = PolicyAcknowledgement.objects.filter(
        user=request.user).select_related("policy")
    serializer = PolicyAcknowledgementSerializer(my_ack, many=True)
    return Response(serializer.data, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pending_acknowledgements(request):
    pending_ack = Policy.objects.filter(is_active=True).exclude(
        acknowledgements__user=request.user,
        acknowledgements__policy_version=F("version"),
    ).select_related("category").distinct()

    serializer = PolicyListSerializer(
        pending_ack,
        many=True,
        context={"request": request},
    )
    return Response(serializer.data, status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_policy_version_view(request, pk):
    """Create a new version of an existing policy and store version history."""
    if request.user.role not in ["ADMIN", "HR"]:
        return Response({"error": "Only Admin or HR can create policy versions."}, status=403)

    policy = get_object_or_404(
        Policy.objects.select_related("category"), id=pk)
    new_version = request.data.get("new_version")
    content = request.data.get("content")
    change_note = request.data.get("change_note", "")
    effective_date = request.data.get("effective_date")

    if not new_version:
        return Response({"error": "new_version is required."}, status=400)
    if content is None:
        return Response({"error": "content is required."}, status=400)

    # Save the current version snapshot before replacing the main policy content.
    PolicyVersionHistory.objects.create(
        policy=policy,
        version=policy.version,
        content=policy.content,
        change_note=f"Previous version captured before upgrade to {new_version}.",
        effective_date=policy.effective_date or timezone.now().date(),
    )

    policy.version = str(new_version)
    policy.content = content
    policy.effective_date = effective_date or policy.effective_date or timezone.now().date()
    policy.status = Policy.PolicyStatus.PUBLISHED
    policy.is_active = True
    policy.save()

    # Store the new version record for version traceability.
    PolicyVersionHistory.objects.create(
        policy=policy,
        version=str(new_version),
        content=content,
        change_note=change_note,
        effective_date=policy.effective_date,
    )

    serializer = PolicyDetailSerializer(policy)
    return Response(serializer.data, status=201)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def archive_policy_view(request, pk):
    """Archive a policy so it is no longer active for employees."""
    if request.user.role not in ["ADMIN", "HR"]:
        return Response({"error": "Only Admin or HR can archive policies."}, status=403)

    policy = get_object_or_404(Policy, id=pk)
    policy.status = Policy.PolicyStatus.ARCHIVED
    policy.is_active = False
    policy.save(update_fields=["status", "is_active", "updated_at"])

    serializer = PolicyDetailSerializer(policy)
    return Response(serializer.data, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def policy_compliance_report_view(request, pk):
    """Return users who have or have not acknowledged the current policy version."""
    if request.user.role not in ["ADMIN", "HR"]:
        return Response({"error": "Only Admin or HR can access compliance reports."}, status=403)

    policy = get_object_or_404(Policy, id=pk)
    active_users = get_user_model().objects.filter(
        is_active=True).select_related("department")

    acknowledgements = PolicyAcknowledgement.objects.filter(
        policy=policy,
        policy_version=policy.version,
    ).select_related("user")

    acknowledged_ids = set(acknowledgements.values_list("user_id", flat=True))
    acknowledged_map = {
        ack.user_id: ack.acknowledged_at.isoformat()
        for ack in acknowledgements
    }

    acknowledged_users = active_users.filter(id__in=acknowledged_ids)
    pending_users = active_users.exclude(id__in=acknowledged_ids)

    acknowledged_data = PolicyComplianceReportSerializer(
        acknowledged_users,
        many=True,
        context={"acknowledged_map": acknowledged_map},
    ).data
    pending_data = PolicyComplianceReportSerializer(
        pending_users,
        many=True,
        context={"acknowledged_map": acknowledged_map},
    ).data

    return Response(
        {
            "acknowledged_users": acknowledged_data,
            "pending_users": pending_data,
        },
        status=200,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_policy_reminder_view(request, pk):
    """Send reminder emails to active users who have not acknowledged the current version."""
    if request.user.role not in ["ADMIN", "HR"]:
        return Response({"error": "Only Admin or HR can send policy reminders."}, status=403)

    policy = get_object_or_404(Policy, id=pk)
    active_users = get_user_model().objects.filter(is_active=True).exclude(
        id__in=PolicyAcknowledgement.objects.filter(
            policy=policy,
            policy_version=policy.version,
        ).values_list("user_id", flat=True)
    )

    reminder_count = 0
    for user in active_users:
        if not user.email:
            continue

        subject = f"Reminder: Please acknowledge policy - {policy.title}"
        message = (
            f"Hello {user.get_full_name() or user.email},\n\n"
            f"This is a reminder to acknowledge the policy '{policy.title}' "
            f"(version {policy.version}).\n"
            f"Please review and acknowledge the latest policy version as soon as possible."
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                  [user.email], fail_silently=False)
        reminder_count += 1

    return Response(
        {
            "detail": "Reminder emails sent successfully.",
            "count": reminder_count,
        },
        status=200,
    )
