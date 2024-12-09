from django.urls import path
from .views import ServiceHealthView, MetricsView, DashboardView, prometheus_metrics

urlpatterns = [
    # Health checks
    path("health/", ServiceHealthView.as_view(), name="service-health"),
    # Metrics
    path("metrics/", MetricsView.as_view(), name="metrics"),
    path("prometheus-metrics/", prometheus_metrics, name="prometheus-metrics"),
    # Dashboard
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
