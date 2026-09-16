from django.urls import path

from .views import accept_invite, create_invite, locked_users, login, login_history, logout, logout_all, me, my_invites, organization_users, password_change, password_reset_confirm, password_reset_request, password_reset_verify, register, resend_invite, token_refresh, unlock_user, verify_invite

urlpatterns = [
    path("token/refresh/", token_refresh, name="token_refresh"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path("logout-all/", logout_all, name="logout_all"),
    path("register/", register, name="register_user"),
    path("me/", me, name="me"),
    path("invites/", create_invite, name="invite_user"),
    path("invites/<int:user_id>/resend/", resend_invite, name="resend_invite"),
    path("invites/verify/", verify_invite, name="verify_invite"),
    path("invites/accept/", accept_invite, name="accept_invite"),
    path("password-reset/request/", password_reset_request,
         name="password_reset_request"),
    path("password-reset/verify/", password_reset_verify,
         name="password_reset_verify"),
    path("password-reset/confirm/", password_reset_confirm,
         name="password_reset_confirm"),
    path("password-change/", password_change, name="password_change"),
    path("users/", organization_users, name="organization_users"),
    path("users/locked/", locked_users, name="locked_users"),
    path("users/<int:user_id>/unlock/", unlock_user, name="unlock_user"),
    path("login-history/", login_history, name="login_history"),
    path("my-invites/", my_invites, name="my_invites"),
]
