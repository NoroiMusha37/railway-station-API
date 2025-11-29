from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/railway/", include("railway.urls", namespace="railway")),
    path("api/v1/user/", include("user.urls", namespace="user")),
    path("__debug__/", include("debug_toolbar.urls")),
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/doc/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui"
    ),
    path(
        "api/v1/doc/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc"
    ),
]
