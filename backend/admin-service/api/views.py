from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
import requests
import logging
from .models import Report, UserWarning, BlockedPost
from .serializers import ReportSerializer, UserWarningSerializer, BlockedPostSerializer
from .permissions import IsAuthenticatedCustom

logger = logging.getLogger(__name__)

# Service URLs (using Docker service names)
USER_SERVICE_URL = "http://user-service:8000"
POST_SERVICE_URL = "http://post-service:8000"


class AdminUserViewSet(APIView):
    """
    ViewSet for managing user-related administrative actions.
    """

    permission_classes = [IsAuthenticatedCustom]

    def get(self, request):
        """
        GET /api/users/
        """
        try:
            response = requests.get(
                f"{USER_SERVICE_URL}/api/users/profile/",
                headers={"Authorization": request.headers.get("Authorization")},
            )
            if response.status_code == 200:
                return Response(response.json())
            return Response(
                {"error": "Failed to fetch users from user service"},
                status=response.status_code,
            )
        except requests.RequestException as e:
            logger.error(f"Failed to fetch users: {str(e)}")
            return Response(
                {"error": "Failed to fetch users from user service"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    def get_user_details(self, request, user_id):
        """
        GET /api/users/<user_id>/
        """
        try:
            response = requests.get(
                f"{USER_SERVICE_URL}/api/users/profile/{user_id}/",
                headers={"Authorization": request.headers.get("Authorization")},
            )
            if response.status_code == 200:
                return Response(response.json())
            return Response(
                {"error": "Failed to fetch user details"}, status=response.status_code
            )
        except requests.RequestException as e:
            logger.error(f"Failed to fetch user details: {str(e)}")
            return Response(
                {"error": "Failed to fetch user details from user service"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    def delete(self, request, user_id):
        """
        DELETE /api/users/<user_id>/
        """
        try:
            # First, delete all user's posts
            posts_response = requests.delete(
                f"{POST_SERVICE_URL}/api/posts/user/{user_id}/",
                headers={"Authorization": request.headers.get("Authorization")},
            )

            # Then, delete the user account
            user_response = requests.delete(
                f"{USER_SERVICE_URL}/api/users/profile/{user_id}/",
                headers={"Authorization": request.headers.get("Authorization")},
            )

            if user_response.status_code == 204:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"error": "Failed to delete user"}, status=user_response.status_code
            )
        except requests.RequestException as e:
            logger.error(f"Failed to delete user: {str(e)}")
            return Response(
                {"error": "Failed to delete user"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


class UserWarningView(APIView):
    """
    View for managing user warnings.
    """

    permission_classes = [IsAuthenticatedCustom]

    def post(self, request, user_id):
        """
        POST /api/users/warn/<user_id>/
        """
        serializer = UserWarningSerializer(
            data={**request.data, "user_id": user_id, "warned_by": request.user}
        )
        if serializer.is_valid():
            warning = serializer.save()

            # Notify user service about the warning
            try:
                response = requests.post(
                    f"{USER_SERVICE_URL}/api/users/profile/{user_id}/warn/",
                    headers={"Authorization": request.headers.get("Authorization")},
                    json={"warning_id": warning.id, "reason": warning.reason},
                )
                if response.status_code != 200:
                    logger.error("Failed to notify user service about warning")
            except requests.RequestException:
                logger.error("Failed to notify user service about warning")
                # Log the error but don't fail the request
                pass

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing content reports.
    """

    permission_classes = [IsAuthenticatedCustom]
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    def get_queryset(self):
        """
        GET /api/reports/
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
        POST /api/reports/<report_id>/resolve/
        """
        report = self.get_object()
        action = request.data.get("action")

        if action not in ["remove", "warn"]:
            return Response(
                {"error": 'Invalid action. Must be either "remove" or "warn"'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Take action based on resolution type
        try:
            if action == "remove":
                # Delete the post
                response = requests.delete(
                    f"{POST_SERVICE_URL}/api/posts/{report.post_id}/",
                    headers={"Authorization": request.headers.get("Authorization")},
                )
                if response.status_code != 204:
                    return Response(
                        {"error": "Failed to delete post"}, status=response.status_code
                    )
            elif action == "warn":
                # Issue a warning to the user
                response = requests.post(
                    f"{USER_SERVICE_URL}/api/users/profile/{report.reported_user}/warn/",
                    headers={"Authorization": request.headers.get("Authorization")},
                    json={"reason": f"Content violation in post {report.post_id}"},
                )
                if response.status_code != 200:
                    return Response(
                        {"error": "Failed to warn user"}, status=response.status_code
                    )
        except requests.RequestException as e:
            logger.error(f"Failed to execute resolution action: {str(e)}")
            return Response(
                {"error": "Failed to execute resolution action"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        report.status = "resolved"
        report.resolved_at = timezone.now()
        report.resolution_action = action
        report.save()

        return Response({"status": "report resolved"})


class AdminPostViewSet(viewsets.ViewSet):
    """
    ViewSet for managing post moderation actions.
    """

    permission_classes = [IsAuthenticatedCustom]

    def list(self, request):
        """
        GET /api/posts/
        """
        try:
            logger.debug(
                f"Making request to post service at {POST_SERVICE_URL}/api/posts/"
            )
            response = requests.get(
                f"{POST_SERVICE_URL}/api/posts/",
                headers={"Authorization": request.headers.get("Authorization")},
            )
            logger.debug(
                f"Post service response: {response.status_code} - {response.text}"
            )
            if response.status_code == 200:
                return Response(response.json())
            return Response(
                {"error": "Failed to fetch posts"}, status=response.status_code
            )
        except requests.RequestException as e:
            logger.error(f"Failed to fetch posts: {str(e)}")
            return Response(
                {"error": "Failed to fetch posts from post service"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    def destroy(self, request, post_id=None):
        """
        DELETE /api/posts/<post_id>/
        """
        try:
            response = requests.delete(
                f"{POST_SERVICE_URL}/api/posts/{post_id}/",
                headers={"Authorization": request.headers.get("Authorization")},
            )
            if response.status_code == 204:
                return Response(status=status.HTTP_204_NO_CONTENT)
            if response.status_code == 404:
                return Response(
                    {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
                )
            return Response(
                {"error": "Failed to delete post"}, status=response.status_code
            )
        except requests.RequestException as e:
            logger.error(f"Failed to delete post: {str(e)}")
            return Response(
                {"error": "Failed to delete post"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    @action(detail=True, methods=["post"])
    def block(self, request, post_id=None):
        """
        POST /api/posts/<post_id>/block/
        """
        duration = request.data.get("duration")  # Duration in hours, optional
        reason = request.data.get("reason")

        expires_at = None
        if duration:
            expires_at = timezone.now() + timedelta(hours=int(duration))

        serializer = BlockedPostSerializer(
            data={
                "post_id": post_id,
                "blocked_by": request.user,
                "duration": duration,
                "reason": reason,
                "expires_at": expires_at,
            }
        )

        if serializer.is_valid():
            blocked_post = serializer.save()

            # Notify post service about the block
            try:
                response = requests.post(
                    f"{POST_SERVICE_URL}/api/posts/{post_id}/block/",
                    headers={"Authorization": request.headers.get("Authorization")},
                    json={
                        "block_id": blocked_post.id,
                        "reason": reason,
                        "expires_at": expires_at.isoformat() if expires_at else None,
                    },
                )
                if response.status_code != 200:
                    logger.error("Failed to notify post service about block")
            except requests.RequestException as e:
                logger.error(f"Failed to notify post service about block: {str(e)}")
                # Log the error but don't fail the request since we've recorded the block
                pass

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
