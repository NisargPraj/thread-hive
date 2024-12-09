from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/admin/", include("api.urls")),
    # Django Prometheus metrics endpoint
    path("", include("django_prometheus.urls")),
]
