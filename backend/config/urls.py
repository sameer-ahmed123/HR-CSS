from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from authentication.views import UserTokenObtainPairView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/token/", UserTokenObtainPairView.as_view(),
         name="token_obtain_pair"),
    path("api/v1/auth/token/refresh/",
         TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/auth/", include("authentication.urls")),
    path("api/v1/organization/", include("organization.urls")),
]
