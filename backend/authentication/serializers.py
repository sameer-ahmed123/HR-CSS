from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import CustomUser


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(email=attrs["email"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")
        attrs["user"] = user
        return attrs


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
                  "role", "phone_number", "is_active")
        read_only_fields = ("id", "email", "role", "is_active")


class UserInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name",
                  "role", "phone_number", "invited_by")
        read_only_fields = ("invited_by",)

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)
