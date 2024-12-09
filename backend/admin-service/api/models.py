from django.db import models


class ServiceHealth(models.Model):
    """
    Model for tracking the health status of microservices.

    This model maintains the current health status of each service in the system,
    including the last successful health check and any error information.

    Attributes:
        service_name (CharField): Name of the service (e.g., 'user-service', 'post-service')
        status (CharField): Current health status of the service
        last_check (DateTimeField): When the service was last checked
        last_successful_check (DateTimeField): When the service last responded successfully
        error_message (TextField): Details of any current error condition
        response_time (FloatField): Last recorded response time in milliseconds
    """

    SERVICE_STATUS_CHOICES = [
        ("healthy", "Healthy"),
        ("degraded", "Degraded"),
        ("down", "Down"),
    ]

    service_name = models.CharField(max_length=100, unique=True)
    status = models.CharField(
        max_length=20, choices=SERVICE_STATUS_CHOICES, default="healthy"
    )
    last_check = models.DateTimeField(auto_now=True)
    last_successful_check = models.DateTimeField(null=True)
    error_message = models.TextField(null=True, blank=True)
    response_time = models.FloatField(null=True)  # in milliseconds

    class Meta:
        verbose_name_plural = "Service health statuses"


class ServiceMetrics(models.Model):
    """
    Model for storing service performance metrics.

    This model captures various performance metrics for each service,
    enabling monitoring and analysis of service behavior over time.

    Attributes:
        service_name (CharField): Name of the service
        timestamp (DateTimeField): When these metrics were recorded
        cpu_usage (FloatField): CPU usage percentage
        memory_usage (FloatField): Memory usage in MB
        request_count (IntegerField): Number of requests handled
        error_count (IntegerField): Number of errors encountered
        average_response_time (FloatField): Average response time in milliseconds
    """

    service_name = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_usage = models.FloatField(null=True)
    memory_usage = models.FloatField(null=True)  # in MB
    request_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    average_response_time = models.FloatField(null=True)  # in milliseconds

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["service_name", "timestamp"]),
        ]
