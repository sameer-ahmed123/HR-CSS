from django.urls import path

from .views import MeView, UserInviteView, UserRegisterView, UserTokenObtainPairView

urlpatterns = [
    path("token/", UserTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("register/", UserRegisterView.as_view(), name="register_user"),
    path("me/", MeView.as_view(), name="me"),
    path("invite/", UserInviteView.as_view(), name="invite_user"),
]
