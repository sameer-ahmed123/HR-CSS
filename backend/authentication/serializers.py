from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import CustomUser, InvitationToken, LoginHistory, PasswordResetToken
from .models import InvitationToken


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs["email"].strip().lower()
        user = CustomUser.objects.filter(email__iexact=email).first()
        if user and not user.is_active:
            raise serializers.ValidationError(
                "This account is inactive. Accept the invitation before signing in.")
        user = authenticate(email=email, password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        attrs["user"] = user
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirmation = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirmation"):
            raise serializers.ValidationError(
                {"password_confirmation": "Passwords do not match."})
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirmation = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs.pop("new_password_confirmation"):
            raise serializers.ValidationError(
                {"new_password_confirmation": "Passwords do not match."})
        return attrs


class LoginHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginHistory
        fields = ("id", "ip_address", "user_agent", "status", "timestamp")


class LockedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "email", "first_name", "last_name", "role",
                  "failed_login_attempts", "locked_at")


class OrganizationUserSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source="department.name", read_only=True, allow_null=True)

    class Meta:
        model = CustomUser
        fields = ("id", "email", "first_name", "last_name", "role",
                  "department_name", "is_active", "created_at")


class SentInviteSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    user_id = serializers.IntegerField(source="id")

    class Meta:
        model = CustomUser
        fields = ("user_id", "email", "role",
                  "is_active", "status", "created_at")

    def get_status(self, obj):
        return "Activated" if obj.is_active else "Pending"


class InviteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "role", "department")

    def validate_email(self, value):
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists.")
        return value


class InviteAcceptSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)


class InviteVerifySerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(
        source="user.first_name", read_only=True)

    class Meta:
        model = InvitationToken
        fields = ("email", "first_name", "expires_at")


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirmation = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "phone_number",
                  "password", "password_confirmation")

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirmation"):
            raise serializers.ValidationError(
                {"password_confirmation": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        return CustomUser.objects.create_user(
            role=CustomUser.Role.EMPLOYEE,
            is_active=True,
            **validated_data,
        )


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "email", "first_name", "last_name",
                  "role", "phone_number", "department", "department_name", "is_active", "created_at")
        read_only_fields = ("id", "email", "role", "is_active", "created_at")
    department_name = serializers.CharField(
        source="department.name", read_only=True, allow_null=True)


class UserInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name",
                  "role", "phone_number", "invited_by")
        read_only_fields = ("invited_by",)

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)
