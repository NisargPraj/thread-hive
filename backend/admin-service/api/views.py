import os
import time
import requests
from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import KafkaError
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
            "user-service": f"{os.getenv('USER_SERVICE_URL')}/api/users/health/",
            "post-service": f"{os.getenv('POST_SERVICE_URL')}/api/posts/health/",
            "kafka": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
        }
        return service_urls.get(service_name)

    def check_kafka_health(self):
        """
        Check Kafka health by attempting to create an admin client connection
        and listing topics
        """
        try:
            start_time = time.time()
            admin_client = KafkaAdminClient(
                bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
                client_id="admin-health-check",
            )

            # Try to list topics to verify connection
            topics = admin_client.list_topics()
            response_time = (time.time() - start_time) * 1000

            admin_client.close()

            return {
                "status": "healthy",
                "response_time": response_time,
                "last_check": timezone.now(),
                "last_successful_check": timezone.now(),
                "error_message": None,
                "topics": len(topics),
            }

        except KafkaError as e:
            return {
                "status": "down",
                "error_message": str(e),
                "last_check": timezone.now(),
                "last_successful_check": None,
                "response_time": None,
            }

    def check_service_health(self, service_name):
        """
        Perform health check for a specific service
        """
        if service_name == "kafka":
            return self.check_kafka_health()

        url = self.get_service_url(service_name)
        if not url:
            return {"status": "down", "error": f"Unknown service: {service_name}"}

        try:
            start_time = time.time()
            response = requests.get(url, timeout=5)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Parse the response to check if the service reports itself as healthy
            try:
                response_data = response.json()
                service_status = response_data.get("status")
                if service_status == "healthy":
                    health_status = {
                        "status": "healthy",
                        "response_time": response_time,
                        "last_check": timezone.now(),
                        "last_successful_check": timezone.now(),
                        "error_message": None,
                    }
                else:
                    health_status = {
                        "status": "degraded",
                        "response_time": response_time,
                        "last_check": timezone.now(),
                        "error_message": response_data.get("error"),
                    }
            except:
                health_status = {
                    "status": "degraded",
                    "response_time": response_time,
                    "last_check": timezone.now(),
                    "error_message": "Invalid response format",
                }

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
        services = ["user-service", "post-service", "kafka"]
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

            # Add Kafka-specific information
            if service == "kafka" and health_check.get("topics") is not None:
                health_statuses[service]["topics"] = health_check["topics"]

        return Response(health_statuses)


class MetricsView(APIView):
    """
    View for collecting and exposing service metrics.
    """

    permission_classes = [AllowAny]

    def get_kafka_metrics(self):
        """Get Kafka metrics through JMX interface"""
        try:
            # Try to get Kafka metrics through JMX
            admin_client = KafkaAdminClient(
                bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
                client_id="admin-metrics",
            )

            topics = admin_client.list_topics()
            metrics = {
                "broker_count": 1,  # Assuming single broker for now
                "topic_count": len(topics),
                "partition_count": 1,  # Default partition count
            }

            admin_client.close()
            return metrics

        except KafkaError as e:
            return {"error": str(e)}

    def get(self, request, format=None):
        """
        GET /api/admin/metrics/

        Retrieve metrics for all services
        """
        metrics = {}
        services = ["user-service", "post-service", "kafka"]

        for service in services:
            # Get the latest metrics
            latest_metrics = (
                ServiceMetrics.objects.filter(service_name=service)
                .order_by("-timestamp")
                .first()
            )

            if service == "kafka":
                kafka_metrics = self.get_kafka_metrics()
                if "error" not in kafka_metrics:
                    metrics["kafka"] = kafka_metrics
                else:
                    metrics["kafka"] = {"status": "No metrics available"}
            elif latest_metrics:
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
        # First, ensure we have up-to-date health checks
        health_view = ServiceHealthView()
        health_data = health_view.get(request).data

        # Get latest metrics for each service
        service_metrics = {}
        services = ["user-service", "post-service", "kafka"]

        for service in services:
            if service == "kafka":
                metrics_view = MetricsView()
                kafka_metrics = metrics_view.get_kafka_metrics()
                if "error" not in kafka_metrics:
                    service_metrics["kafka"] = kafka_metrics
            else:
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
            "service_health": health_data,
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
