from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/railway/", include("railway.urls", namespace="railway")),
    path("api/v1/user/", include("user.urls", namespace="user")),
    path("__debug__/", include("debug_toolbar.urls"))
]
