from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("authentication.urls")),
    path("api/v1/organization/", include("organization.urls")),
    path("api/v1/recruitment/", include("recruitment.urls")),
    path("api/v1/documents/",include("documents.urls")),
    path('api/v1/policies/',include("policies.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
