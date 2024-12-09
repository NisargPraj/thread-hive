from django.contrib import admin
from .models import ServiceHealth, ServiceMetrics


@admin.register(ServiceHealth)
class ServiceHealthAdmin(admin.ModelAdmin):
    """Admin interface configuration for ServiceHealth model."""

    list_display = (
        "service_name",
        "status",
        "last_check",
        "last_successful_check",
        "response_time",
    )
    list_filter = ("status", "last_check", "last_successful_check")
    search_fields = ("service_name", "error_message")
    readonly_fields = ("last_check", "last_successful_check")
    ordering = ("service_name",)


@admin.register(ServiceMetrics)
class ServiceMetricsAdmin(admin.ModelAdmin):
    """Admin interface configuration for ServiceMetrics model."""

    list_display = (
        "service_name",
        "timestamp",
        "cpu_usage",
        "memory_usage",
        "request_count",
        "error_count",
        "average_response_time",
    )
    list_filter = ("service_name", "timestamp")
    search_fields = ("service_name",)
    readonly_fields = ("timestamp",)
    ordering = ("-timestamp",)
