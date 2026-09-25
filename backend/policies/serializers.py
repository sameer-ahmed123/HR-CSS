from rest_framework import serializers
from policies.models import *


class PolicyCategorySerializer(serializers.ModelSerializer):

    total_policies = serializers.IntegerField(read_only=True)

    class Meta:
        model = PolicyCategory
        fields = [
            'id',
            'name',
            'description',
            'total_policies'
        ]


class PolicyListSerializer(serializers.ModelSerializer):
    is_acknowledged = serializers.SerializerMethodField()

    class Meta:
        model = Policy
        fields = [
            'id',
            'title',
            'version',
            'is_mandatory',
            'is_acknowledged'
        ]

    def get_is_acknowledged(self, obj):
        request = self.context.get("request")
        if not request or not request.user or request.user.is_anonymous:
            return False

        if hasattr(obj, "is_acknowledged"):
            return bool(obj.is_acknowledged)

        return obj.acknowledgements.filter(user=request.user).exists()


class PolicyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = '__all__'


class PolicyAcknowledgementSerializer(serializers.ModelSerializer):
    policy_title = serializers.CharField(source="policy.title", read_only=True)
    policy_version = serializers.CharField(
        source="policy.version", read_only=True)

    class Meta:
        model = PolicyAcknowledgement
        fields = [
            'id',
            'policy_title',
            'policy_version',
            'acknowledged_at'
        ]
