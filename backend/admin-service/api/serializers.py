from rest_framework import serializers
from .models import ServiceHealth, ServiceMetrics


class ServiceHealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceHealth
        fields = "__all__"
        read_only_fields = ("last_check",)


class ServiceMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceMetrics
        fields = "__all__"
        read_only_fields = ("timestamp",)
