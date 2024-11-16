"""
Main URL Configuration for the Admin Service

This module defines the top-level URL patterns for the entire admin service.
It includes both the Django admin interface (renamed to avoid conflicts)
and our custom admin API endpoints.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django's built-in admin interface
    # Renamed from 'admin/' to 'django-admin/' to avoid conflict with our API
    path("django-admin/", admin.site.urls),
    # Our custom admin API endpoints
    # All endpoints under this path require authentication
    # Available endpoints:
    # - User Management:
    #   * GET    /api/admin/users/
    #   * GET    /api/admin/users/<user_id>/
    #   * DELETE /api/admin/users/<user_id>/
    #   * POST   /api/admin/users/warn/<user_id>/
    #
    # - Report Management:
    #   * GET    /api/admin/reports/
    #   * POST   /api/admin/reports/<report_id>/resolve/
    #
    # - Post Management:
    #   * DELETE /api/admin/posts/<post_id>/
    #   * POST   /api/admin/posts/<post_id>/block/
    path("api/admin/", include("api.urls")),
]
