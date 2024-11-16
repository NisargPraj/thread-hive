from rest_framework import serializers
from .models import Report, UserWarning, BlockedPost


class ReportSerializer(serializers.ModelSerializer):
    """
    Serializer for the Report model.

    Handles the conversion between Report model instances and JSON representations.
    Automatically includes all fields from the Report model while making certain
    fields read-only to prevent modification through the API.

    Read-only fields:
        - report_id: Generated automatically
        - created_at: Set automatically when report is created
        - resolved_at: Set automatically when report is resolved
    """

    class Meta:
        model = Report
        fields = "__all__"
        read_only_fields = ("report_id", "created_at", "resolved_at")


class UserWarningSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserWarning model.

    Converts UserWarning model instances to and from JSON format for the API.
    The created_at timestamp is read-only as it's automatically set when
    a warning is created.

    Read-only fields:
        - created_at: Set automatically when warning is created
    """

    class Meta:
        model = UserWarning
        fields = "__all__"
        read_only_fields = ("created_at",)


class BlockedPostSerializer(serializers.ModelSerializer):
    """
    Serializer for the BlockedPost model.

    Handles serialization and deserialization of BlockedPost instances.
    Includes validation for the duration field to ensure it's a positive number
    when provided.

    Read-only fields:
        - blocked_at: Set automatically when post is blocked
        - expires_at: Calculated based on blocked_at and duration

    Validation:
        - duration: Must be a positive number if provided
    """

    class Meta:
        model = BlockedPost
        fields = "__all__"
        read_only_fields = ("blocked_at", "expires_at")

    def validate_duration(self, value):
        """
        Validate that the block duration is a positive number.

        Args:
            value: The duration value to validate

        Returns:
            The validated duration value

        Raises:
            serializers.ValidationError: If duration is not positive
        """
        if value is not None and value <= 0:
            raise serializers.ValidationError("Duration must be a positive number")
        return value
