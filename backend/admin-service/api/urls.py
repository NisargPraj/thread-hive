from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for ViewSets
router = DefaultRouter()

# Register the reports endpoint with the router
# This automatically creates the following URL patterns:
# - GET /reports/ - List all reports
# - POST /reports/ - Create a new report
# - GET /reports/{id}/ - Retrieve a specific report
# - PUT /reports/{id}/ - Update a specific report
# - PATCH /reports/{id}/ - Partially update a specific report
# - DELETE /reports/{id}/ - Delete a specific report
# - POST /reports/{id}/resolve/ - Custom action to resolve a report
router.register(r"reports", views.ReportViewSet, basename="report")

# URL patterns for the admin API
urlpatterns = [
    # User Management Endpoints
    # -----------------------
    # GET: Retrieve list of all users
    path("users/", views.AdminUserViewSet.as_view(), name="admin-users-list"),
    # GET: Retrieve specific user details
    # DELETE: Suspend/delete a specific user
    path(
        "users/<str:user_id>/",
        views.AdminUserViewSet.as_view(),
        name="admin-user-detail",
    ),
    # POST: Issue a warning to a specific user
    # Request body should include:
    # - reason: Why the warning is being issued
    path(
        "users/warn/<str:user_id>/", views.UserWarningView.as_view(), name="warn-user"
    ),
    # Post Management Endpoints
    # -----------------------
    # DELETE: Remove an inappropriate post
    path(
        "posts/<str:post_id>/",
        views.AdminPostViewSet.as_view({"delete": "destroy"}),
        name="delete-post",
    ),
    # POST: Temporarily hide a post
    # Request body can include:
    # - duration: How long to hide the post (in hours)
    # - reason: Why the post is being hidden
    path(
        "posts/<str:post_id>/block/",
        views.AdminPostViewSet.as_view({"post": "block"}),
        name="block-post",
    ),
    # Include all routes registered with the router
    # This adds all the report-related endpoints
    path("", include(router.urls)),
]
