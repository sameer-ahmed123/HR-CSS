from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    UserInviteSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserRegisterSerializer,
)


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        return token


class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer


class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = (permissions.AllowAny,)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserInviteView(generics.CreateAPIView):
    serializer_class = UserInviteSerializer
    permission_classes = (permissions.IsAdminUser,)

    def perform_create(self, serializer):
        serializer.save(invited_by=self.request.user)
