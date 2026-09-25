from django.contrib.auth import get_user_model
from rest_framework import serializers

from policies.models import (
    Policy,
    PolicyAcknowledgement,
    PolicyCategory,
    PolicyVersionHistory,
)


class PolicyCategorySerializer(serializers.ModelSerializer):
    total_policies = serializers.IntegerField(read_only=True)

    class Meta:
        model = PolicyCategory
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "total_policies",
        ]


class PolicyVersionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyVersionHistory
        fields = [
            "id",
            "policy",
            "version",
            "content",
            "change_note",
            "effective_date",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class PolicyListSerializer(serializers.ModelSerializer):
    is_acknowledged = serializers.SerializerMethodField()

    class Meta:
        model = Policy
        fields = [
            "id",
            "category",
            "title",
            "version",
            "status",
            "effective_date",
            "is_mandatory",
            "is_active",
            "is_acknowledged",
        ]

    def get_is_acknowledged(self, obj):
        request = self.context.get("request")
        if not request or not request.user or request.user.is_anonymous:
            return False

        return obj.acknowledgements.filter(
            user=request.user,
            policy_version=obj.version,
        ).exists()


class PolicyDetailSerializer(serializers.ModelSerializer):
    version_history = PolicyVersionHistorySerializer(
        many=True,
        read_only=True,
        source="version_history",
    )

    class Meta:
        model = Policy
        fields = [
            "id",
            "category",
            "title",
            "content",
            "document_file",
            "version",
            "effective_date",
            "status",
            "created_by",
            "is_mandatory",
            "is_active",
            "version_history",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "version_history",
        ]


class PolicyComplianceReportSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    acknowledged = serializers.SerializerMethodField()
    acknowledged_at = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "full_name",
            "email",
            "department",
            "acknowledged",
            "acknowledged_at",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.email

    def get_department(self, obj):
        return obj.department.name if getattr(obj, "department", None) else None

    def get_acknowledged(self, obj):
        acknowledged_map = self.context.get("acknowledged_map", {})
        return obj.id in acknowledged_map

    def get_acknowledged_at(self, obj):
        acknowledged_map = self.context.get("acknowledged_map", {})
        return acknowledged_map.get(obj.id)


class PolicyAcknowledgementSerializer(serializers.ModelSerializer):
    policy_title = serializers.CharField(source="policy.title", read_only=True)

    class Meta:
        model = PolicyAcknowledgement
        fields = [
            "id",
            "policy",
            "policy_title",
            "policy_version",
            "acknowledged_at",
        ]
        read_only_fields = ["id", "acknowledged_at", "policy_title"]
