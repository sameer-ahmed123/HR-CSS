import hashlib
import secrets
import smtplib
from datetime import timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework.exceptions import APIException

from .models import InvitationToken, PasswordResetToken


INVITATION_LIFETIME = timedelta(hours=48)
PASSWORD_RESET_LIFETIME = timedelta(hours=1)


class InvitationEmailDeliveryError(APIException):
    status_code = 503
    default_detail = "The invitation could not be delivered. Check the SMTP configuration and try again."
    default_code = "email_delivery_unavailable"


def _hash_token(raw_token):
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def create_invitation(user, inviter):
    raw_token = secrets.token_urlsafe(32)
    invitation, _ = InvitationToken.objects.update_or_create(
        user=user,
        defaults={
            "token_hash": _hash_token(raw_token),
            "expires_at": timezone.now() + INVITATION_LIFETIME,
            "used_at": None,
        },
    )
    send_invitation_email(user, inviter, raw_token, invitation.expires_at)
    return invitation


def send_invitation_email(user, inviter, raw_token, expires_at):
    invite_url = f"{settings.INVITE_URL_BASE}?token={raw_token}"
    context = {
        "first_name": user.first_name,
        "inviter_name": inviter.get_full_name() or inviter.email,
        "invite_url": invite_url,
        "expiry_hours": 48,
    }
    html_body = render_to_string("emails/invite_user.html", context)
    text_body = (
        f"Hello {user.first_name},\n\n"
        f"{context['inviter_name']} invited you to join HR-CSS.\n"
        f"Set your password here: {invite_url}\n\n"
        "This invitation expires in 48 hours."
    )
    message = EmailMultiAlternatives(
        subject="You have been invited to HR-CSS",
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    message.attach_alternative(html_body, "text/html")
    try:
        message.send(fail_silently=False)
    except (smtplib.SMTPException, OSError) as error:
        raise InvitationEmailDeliveryError() from error


def get_valid_invitation(raw_token):
    try:
        invitation = InvitationToken.objects.select_related("user").get(
            token_hash=_hash_token(raw_token)
        )
    except InvitationToken.DoesNotExist:
        return None
    return invitation if invitation.is_valid else None


def create_password_reset(user):
    PasswordResetToken.objects.filter(
        user=user, used_at__isnull=True).update(used_at=timezone.now())
    raw_token = secrets.token_urlsafe(32)
    reset_token = PasswordResetToken.objects.create(
        user=user,
        token_hash=_hash_token(raw_token),
        expires_at=timezone.now() + PASSWORD_RESET_LIFETIME,
    )
    reset_url = f"{settings.RESET_URL_BASE}?token={raw_token}"
    context = {"first_name": user.first_name,
               "reset_url": reset_url, "expiry_hours": 1}
    html_body = render_to_string("emails/password_reset.html", context)
    text_body = (
        f"Hello {user.first_name},\n\nReset your HR-CSS password here: {reset_url}\n\n"
        "This link expires in 1 hour."
    )
    message = EmailMultiAlternatives(
        subject="Reset your HR-CSS password",
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    message.attach_alternative(html_body, "text/html")
    try:
        message.send(fail_silently=False)
    except (smtplib.SMTPException, OSError) as error:
        reset_token.delete()
        raise InvitationEmailDeliveryError(
            "The password reset email could not be delivered.") from error
    return reset_token


def get_valid_password_reset(raw_token):
    try:
        reset_token = PasswordResetToken.objects.select_related("user").get(
            token_hash=_hash_token(raw_token)
        )
    except PasswordResetToken.DoesNotExist:
        return None
    return reset_token if reset_token.is_valid else None
