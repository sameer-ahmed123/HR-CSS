from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from common.permissions import IsAdminOrHR

from .models import CustomUser, LoginHistory
from .serializers import (
    InviteAcceptSerializer,
    InviteCreateSerializer,
    InviteVerifySerializer,
    LockedUserSerializer,
    LoginHistorySerializer,
    OrganizationUserSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    SentInviteSerializer,
    UserProfileSerializer,
    UserRegisterSerializer,
)
from .services import (
    InvitationEmailDeliveryError,
    create_invitation,
    create_password_reset,
    get_valid_invitation,
    get_valid_password_reset,
)


def token_response(user):
    refresh = TokenObtainPairSerializer.get_token(user)
    refresh["role"] = user.role
    refresh["email"] = user.email
    return {"access": str(refresh.access_token), "refresh": str(refresh), "user": UserProfileSerializer(user).data}


def request_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    return forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")


def invalidate_user_tokens(user):
    for outstanding in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=outstanding)


"""
AUTHENTICATION VIEWS
"""


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def token_refresh(request):
    serializer = TokenRefreshSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.validated_data)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login(request):
    email = str(request.data.get("email", "")).strip().lower()
    password = request.data.get("password", "")
    user = CustomUser.objects.filter(email__iexact=email).first()
    history_status = LoginHistory.Status.FAILED
    if user:
        if user.is_locked:
            LoginHistory.objects.create(user=user, ip_address=request_ip(
                request), user_agent=request.META.get("HTTP_USER_AGENT", ""), status=history_status)
            return Response({"detail": "This account is locked. Contact HR or an administrator."}, status=status.HTTP_423_LOCKED)
        authenticated = authenticate(
            request=request, email=email, password=password)
        if authenticated and user.is_active:
            user.failed_login_attempts = 0
            user.is_locked = False
            user.locked_at = None
            user.save(update_fields=[
                      "failed_login_attempts", "is_locked", "locked_at"])
            LoginHistory.objects.create(user=user, ip_address=request_ip(
                request), user_agent=request.META.get("HTTP_USER_AGENT", ""), status=LoginHistory.Status.SUCCESS)
            return Response(token_response(user))
        if not user.is_active:
            detail = "This account is inactive. Accept the invitation before signing in."
        else:
            detail = "Invalid email or password."
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.is_locked = True
            user.locked_at = timezone.now()
        user.save(update_fields=[
                  "failed_login_attempts", "is_locked", "locked_at"])
        LoginHistory.objects.create(user=user, ip_address=request_ip(
            request), user_agent=request.META.get("HTTP_USER_AGENT", ""), status=history_status)
        return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"detail": "Invalid email or password."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(UserProfileSerializer(serializer.save()).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    refresh = request.data.get("refresh")
    if not refresh:
        return Response({"detail": "A refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        token = RefreshToken(refresh)
        if str(token.get("user_id")) != str(request.user.id):
            return Response({"detail": "Token does not belong to this user."}, status=status.HTTP_403_FORBIDDEN)
        token.blacklist()
    except TokenError:
        return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout_all(request):
    invalidate_user_tokens(request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)


"""
USER PROFILE VIEWS
"""


@api_view(["GET", "PATCH"])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    if request.method == "PATCH":
        serializer = UserProfileSerializer(
            request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    return Response(UserProfileSerializer(request.user).data)


"""
Invitation and Password Reset Views
"""


@api_view(["POST"])
@permission_classes([IsAdminOrHR])
def create_invite(request):
    serializer = InviteCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    requested_role = serializer.validated_data['role']
    if requested_role == CustomUser.Role.ADMIN and request.user.role != CustomUser.Role.ADMIN:
        return Response({"detail": "HR users cannot invite administrators."},
                        status=status.HTTP_403_FORBIDDEN,)
    with transaction.atomic():
        user = serializer.save(invited_by=request.user, is_active=False)
        user.set_unusable_password()
        user.save(update_fields=["password"])
        create_invitation(user, request.user)
    return Response(UserProfileSerializer(user).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAdminOrHR])
def resend_invite(request, user_id):
    user = CustomUser.objects.filter(pk=user_id, is_active=False).first()
    if not user:
        return Response({"detail": "Pending invite not found."}, status=status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        create_invitation(user, request.user)
    return Response({"detail": "Invitation resent."})


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def verify_invite(request):
    invitation = get_valid_invitation(request.query_params.get("token", ""))
    if not invitation:
        return Response({"detail": "This invitation is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)
    return Response(InviteVerifySerializer(invitation).data)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def accept_invite(request):
    serializer = InviteAcceptSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    invitation = get_valid_invitation(serializer.validated_data["token"])
    if not invitation:
        return Response({"detail": "This invitation is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)
    with transaction.atomic():
        user = invitation.user
        user.set_password(serializer.validated_data["password"])
        user.is_active = True
        user.save(update_fields=["password", "is_active", "updated_at"])
        invitation.used_at = timezone.now()
        invitation.save(update_fields=["used_at", "updated_at"])
    return Response(token_response(user))


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def password_reset_request(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = CustomUser.objects.filter(
        email__iexact=serializer.validated_data["email"].strip()).first()
    if user and user.is_active:
        create_password_reset(user)
    return Response({"detail": "If an active account exists for that email, a reset link has been sent."})


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def password_reset_verify(request):
    if not get_valid_password_reset(request.query_params.get("token", "")):
        return Response({"detail": "This reset link is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"valid": True})


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def password_reset_confirm(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    reset_token = get_valid_password_reset(serializer.validated_data["token"])
    if not reset_token:
        return Response({"detail": "This reset link is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)
    with transaction.atomic():
        user = reset_token.user
        user.set_password(serializer.validated_data["password"])
        user.failed_login_attempts = 0
        user.is_locked = False
        user.locked_at = None
        user.save(update_fields=[
                  "password", "failed_login_attempts", "is_locked", "locked_at", "updated_at"])
        reset_token.used_at = timezone.now()
        reset_token.save(update_fields=["used_at", "updated_at"])
        invalidate_user_tokens(user)
    return Response(token_response(user))


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def password_change(request):
    serializer = PasswordChangeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    if not request.user.check_password(serializer.validated_data["old_password"]):
        return Response({"old_password": ["Current password is incorrect."]}, status=status.HTTP_400_BAD_REQUEST)
    request.user.set_password(serializer.validated_data["new_password"])
    request.user.save(update_fields=["password", "updated_at"])
    invalidate_user_tokens(request.user)
    return Response({"detail": "Password changed successfully."})


"""
Access Control Views
"""


@api_view(["POST"])
@permission_classes([IsAdminOrHR])
def unlock_user(request, user_id):
    user = CustomUser.objects.filter(pk=user_id).first()
    if not user:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    user.failed_login_attempts = 0
    user.is_locked = False
    user.locked_at = None
    user.save(update_fields=["failed_login_attempts",
              "is_locked", "locked_at"])
    return Response({"detail": "User unlocked."})


@api_view(["GET"])
@permission_classes([IsAdminOrHR])
def locked_users(request):
    users = CustomUser.objects.filter(
        is_locked=True).order_by("locked_at", "email")
    return Response(LockedUserSerializer(users, many=True).data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def organization_users(request):
    users = CustomUser.objects.select_related("department").order_by(
        "last_name", "first_name", "email")
    return Response(OrganizationUserSerializer(users, many=True).data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def login_history(request):
    logs = LoginHistory.objects.filter(user=request.user)[:50]
    return Response(LoginHistorySerializer(logs, many=True).data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def my_invites(request):
    invites = CustomUser.objects.filter(
        invited_by=request.user).order_by("-created_at")
    return Response(SentInviteSerializer(invites, many=True).data)
