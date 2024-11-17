from django.db import models


class Report(models.Model):
    """
    Model for handling reported content in the system.

    This model stores information about reported posts, including who reported them,
    the reason for the report, and the current status of the report.

    Attributes:
        report_id (AutoField): Primary key for the report
        post_id (CharField): ID of the reported post
        reporter_id (CharField): ID of the user who made the report
        reason (TextField): Detailed explanation of why the post was reported
        status (CharField): Current status of the report (pending/resolved)
        created_at (DateTimeField): When the report was created
        resolved_at (DateTimeField): When the report was resolved (if applicable)
        resolution_action (CharField): What action was taken to resolve the report
    """

    REPORT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("resolved", "Resolved"),
    ]

    report_id = models.AutoField(primary_key=True)
    post_id = models.CharField(max_length=255)
    reporter_id = models.CharField(max_length=255)
    reason = models.TextField()
    status = models.CharField(
        max_length=20, choices=REPORT_STATUS_CHOICES, default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_action = models.CharField(
        max_length=50, null=True, blank=True
    )  # e.g., 'remove', 'warn'

    class Meta:
        ordering = ["-created_at"]


class UserWarning(models.Model):
    """
    Model for storing warnings issued to users by administrators.

    This model keeps track of official warnings given to users for inappropriate
    behavior or content violations.

    Attributes:
        user_id (CharField): ID of the warned user
        reason (TextField): Explanation of why the warning was issued
        created_at (DateTimeField): When the warning was issued
        warned_by (CharField): ID of the admin who issued the warning
    """

    user_id = models.CharField(max_length=255)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    warned_by = models.CharField(max_length=255)  # Admin who issued the warning

    class Meta:
        ordering = ["-created_at"]


class BlockedPost(models.Model):
    """
    Model for managing temporarily or permanently blocked posts.

    This model handles posts that have been hidden from users due to content
    violations or other administrative actions.

    Attributes:
        post_id (CharField): ID of the blocked post
        blocked_at (DateTimeField): When the post was blocked
        blocked_by (CharField): ID of the admin who blocked the post
        duration (IntegerField): How long the post should be blocked (in hours)
        reason (TextField): Why the post was blocked
        expires_at (DateTimeField): When the block expires (null for permanent blocks)
    """

    post_id = models.CharField(max_length=255, unique=True)
    blocked_at = models.DateTimeField(auto_now_add=True)
    blocked_by = models.CharField(max_length=255)  # Admin who blocked the post
    duration = models.IntegerField(
        null=True, blank=True
    )  # Duration in hours, null for permanent
    reason = models.TextField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-blocked_at"]
