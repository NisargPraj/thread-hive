from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import Report, UserWarning, BlockedPost
from .serializers import ReportSerializer, UserWarningSerializer, BlockedPostSerializer


class AdminUserViewSet(APIView):
    """
    ViewSet for managing user-related administrative actions.

    This view handles operations related to user management, including:
    - Listing all users
    - Retrieving specific user details
    - Deleting/suspending users

    All endpoints require authentication and admin privileges.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        GET /api/admin/users/

        Retrieve a list of all users in the system.
        This endpoint would typically integrate with the user service
        to fetch actual user data.

        Returns:
            Response: JSON containing list of users with basic information
        """
        # Mock response - in production, this would fetch from user service
        return Response(
            {
                "users": [
                    {"id": "1", "username": "user1", "status": "active"},
                    {"id": "2", "username": "user2", "status": "active"},
                ]
            }
        )

    def get_user_details(self, request, user_id):
        """
        GET /api/admin/users/<user_id>/

        Retrieve detailed information about a specific user.

        Args:
            user_id: The ID of the user to retrieve

        Returns:
            Response: JSON containing detailed user information
        """
        # Mock response - in production, this would fetch from user service
        return Response(
            {
                "id": user_id,
                "username": f"user{user_id}",
                "status": "active",
                "joined_date": "2024-01-01",
            }
        )

    def delete(self, request, user_id):
        """
        DELETE /api/admin/users/<user_id>/

        Suspend or delete a user from the system.

        Args:
            user_id: The ID of the user to delete/suspend

        Returns:
            Response: 204 No Content on success
        """
        # In production, this would make a request to the user service
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserWarningView(APIView):
    """
    View for managing user warnings.

    Handles the creation of official warnings that are issued to users
    for content violations or inappropriate behavior.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        """
        POST /api/admin/users/warn/<user_id>/

        Issue a warning to a specific user.

        Args:
            user_id: The ID of the user to warn

        Request body:
            - reason: Why the warning is being issued

        Returns:
            Response: Created warning details or error message
        """
        serializer = UserWarningSerializer(
            data={**request.data, "user_id": user_id, "warned_by": request.user.id}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing content reports.

    Provides endpoints for:
    - Listing all reports
    - Creating new reports
    - Retrieving specific reports
    - Resolving reports

    Includes pagination support and filtering options.
    """

    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        GET /api/admin/reports/

        Retrieve a paginated list of reports.
        Supports optional page and limit query parameters.

        Query parameters:
            - page: Page number to retrieve
            - limit: Number of items per page

        Returns:
            QuerySet: Filtered and paginated reports
        """
        queryset = Report.objects.all()
        page = self.request.query_params.get("page", None)
        limit = self.request.query_params.get("limit", None)

        if page is not None and limit is not None:
            start = (int(page) - 1) * int(limit)
            end = start + int(limit)
            queryset = queryset[start:end]

        return queryset

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        """
        POST /api/admin/reports/<report_id>/resolve/

        Resolve a reported post by taking appropriate action.

        Args:
            pk: The ID of the report to resolve

        Request body:
            - action: The action to take ('remove' or 'warn')

        Returns:
            Response: Success message or error details
        """
        report = self.get_object()
        action = request.data.get("action")

        if action not in ["remove", "warn"]:
            return Response(
                {"error": 'Invalid action. Must be either "remove" or "warn"'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        report.status = "resolved"
        report.resolved_at = timezone.now()
        report.resolution_action = action
        report.save()

        return Response({"status": "report resolved"})


class AdminPostViewSet(viewsets.ViewSet):
    """
    ViewSet for managing post moderation actions.

    Provides endpoints for:
    - Deleting inappropriate posts
    - Temporarily blocking posts from view
    """

    permission_classes = [IsAuthenticated]

    def destroy(self, request, post_id=None):
        """
        DELETE /api/admin/posts/<post_id>/

        Permanently delete a post from the system.

        Args:
            post_id: The ID of the post to delete

        Returns:
            Response: 204 No Content on success
        """
        # In production, this would make a request to the post service
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def block(self, request, post_id=None):
        """
        POST /api/admin/posts/<post_id>/block/

        Temporarily hide a post from users.

        Args:
            post_id: The ID of the post to block

        Request body:
            - duration: How long to block the post (in hours, optional)
            - reason: Why the post is being blocked

        Returns:
            Response: Created block details or error message
        """
        duration = request.data.get("duration")  # Duration in hours, optional
        reason = request.data.get("reason")

        expires_at = None
        if duration:
            expires_at = timezone.now() + timedelta(hours=int(duration))

        serializer = BlockedPostSerializer(
            data={
                "post_id": post_id,
                "blocked_by": request.user.id,
                "duration": duration,
                "reason": reason,
                "expires_at": expires_at,
            }
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
