from django.contrib import admin
from .models import Report, UserWarning, BlockedPost


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin interface configuration for Report model."""

    list_display = (
        "report_id",
        "post_id",
        "reporter_id",
        "status",
        "created_at",
        "resolved_at",
    )
    list_filter = ("status", "created_at", "resolved_at")
    search_fields = ("post_id", "reporter_id", "reason")
    readonly_fields = ("created_at", "resolved_at")
    ordering = ("-created_at",)


@admin.register(UserWarning)
class UserWarningAdmin(admin.ModelAdmin):
    """Admin interface configuration for UserWarning model."""

    list_display = ("user_id", "warned_by", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user_id", "warned_by", "reason")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


@admin.register(BlockedPost)
class BlockedPostAdmin(admin.ModelAdmin):
    """Admin interface configuration for BlockedPost model."""

    list_display = ("post_id", "blocked_by", "blocked_at", "duration", "expires_at")
    list_filter = ("blocked_at", "expires_at")
    search_fields = ("post_id", "blocked_by", "reason")
    readonly_fields = ("blocked_at",)
    ordering = ("-blocked_at",)
