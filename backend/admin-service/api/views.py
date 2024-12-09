import os
import time
import requests
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
from django.utils import timezone
from .models import ServiceHealth, ServiceMetrics
from .serializers import ServiceHealthSerializer, ServiceMetricsSerializer

# Prometheus metrics
REQUEST_COUNT = Counter(
    "request_count_total", "Total request count", ["service", "endpoint"]
)
REQUEST_LATENCY = Histogram(
    "request_latency_seconds", "Request latency", ["service", "endpoint"]
)


class ServiceHealthView(APIView):
    """
    View for managing service health checks and monitoring.
    """

    permission_classes = [AllowAny]

    def get_service_url(self, service_name):
        """Helper method to get service URLs from environment variables"""
        service_urls = {
            "user-service": f"{os.getenv('USER_SERVICE_URL')}/health/",
            "post-service": f"{os.getenv('POST_SERVICE_URL')}/health/",
            "kafka-consumer": f"{os.getenv('KAFKA_CONSUMER_URL')}/health/",
        }
        return service_urls.get(service_name)

    def check_service_health(self, service_name):
        """
        Perform health check for a specific service
        """
        url = self.get_service_url(service_name)
        if not url:
            return {"status": "down", "error": f"Unknown service: {service_name}"}

        try:
            start_time = time.time()
            response = requests.get(url, timeout=5)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            health_status = {
                "status": "healthy" if response.status_code == 200 else "degraded",
                "response_time": response_time,
                "last_check": timezone.now(),
                "error_message": None,
            }

            if response.status_code == 200:
                health_status["last_successful_check"] = timezone.now()

            return health_status

        except requests.RequestException as e:
            return {
                "status": "down",
                "error_message": str(e),
                "last_check": timezone.now(),
            }

    def get(self, request):
        """
        GET /api/admin/health/

        Retrieve health status for all services
        """
        services = ["user-service", "post-service", "kafka-consumer"]
        health_statuses = {}

        for service in services:
            health_check = self.check_service_health(service)

            # Update or create ServiceHealth record
            service_health, _ = ServiceHealth.objects.update_or_create(
                service_name=service,
                defaults={
                    "status": health_check["status"],
                    "error_message": health_check.get("error_message"),
                    "response_time": health_check.get("response_time"),
                    "last_successful_check": health_check.get("last_successful_check"),
                },
            )

            health_statuses[service] = {
                "status": service_health.status,
                "last_check": service_health.last_check,
                "last_successful_check": service_health.last_successful_check,
                "response_time": service_health.response_time,
                "error_message": service_health.error_message,
            }

        return Response(health_statuses)


class MetricsView(APIView):
    """
    View for collecting and exposing service metrics.
    """

    permission_classes = [AllowAny]

    def get(self, request, format=None):
        """
        GET /api/admin/metrics/

        Retrieve metrics for all services
        """
        metrics = {}
        services = ["user-service", "post-service", "kafka-consumer"]

        for service in services:
            # Get the latest metrics for each service
            latest_metrics = (
                ServiceMetrics.objects.filter(service_name=service)
                .order_by("-timestamp")
                .first()
            )

            if latest_metrics:
                metrics[service] = {
                    "cpu_usage": latest_metrics.cpu_usage,
                    "memory_usage": latest_metrics.memory_usage,
                    "request_count": latest_metrics.request_count,
                    "error_count": latest_metrics.error_count,
                    "average_response_time": latest_metrics.average_response_time,
                    "timestamp": latest_metrics.timestamp,
                }
            else:
                metrics[service] = {"status": "No metrics available"}

        return Response(metrics)

    def post(self, request):
        """
        POST /api/admin/metrics/

        Record new metrics for a service
        """
        service_name = request.data.get("service_name")
        if not service_name:
            return Response(
                {"error": "service_name is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        metrics = ServiceMetrics.objects.create(
            service_name=service_name,
            cpu_usage=request.data.get("cpu_usage"),
            memory_usage=request.data.get("memory_usage"),
            request_count=request.data.get("request_count", 0),
            error_count=request.data.get("error_count", 0),
            average_response_time=request.data.get("average_response_time"),
        )

        return Response(
            {
                "message": f"Metrics recorded for {service_name}",
                "metrics_id": metrics.id,
            },
            status=status.HTTP_201_CREATED,
        )


class DashboardView(APIView):
    """
    View for the admin dashboard, providing system-wide statistics and status.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        """
        GET /api/admin/dashboard/

        Retrieve dashboard data including service health, metrics, and system statistics
        """
        # Get service health status
        service_health = {
            health.service_name: health.status for health in ServiceHealth.objects.all()
        }

        # Get latest metrics for each service
        service_metrics = {}
        for service in ServiceHealth.objects.values_list("service_name", flat=True):
            latest_metric = (
                ServiceMetrics.objects.filter(service_name=service)
                .order_by("-timestamp")
                .first()
            )

            if latest_metric:
                service_metrics[service] = {
                    "cpu_usage": latest_metric.cpu_usage,
                    "memory_usage": latest_metric.memory_usage,
                    "request_count": latest_metric.request_count,
                    "error_count": latest_metric.error_count,
                    "average_response_time": latest_metric.average_response_time,
                }

        dashboard_data = {
            "service_health": service_health,
            "service_metrics": service_metrics,
            "timestamp": timezone.now(),
        }

        return Response(dashboard_data)


@api_view(["GET"])
def prometheus_metrics(request):
    """
    GET /api/admin/prometheus-metrics/

    Endpoint for exposing Prometheus metrics
    """
    metrics_page = generate_latest()
    return HttpResponse(metrics_page, content_type=CONTENT_TYPE_LATEST)
