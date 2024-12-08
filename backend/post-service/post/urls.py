from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    PostViewSet,
    SpecificPostViewSet,
    LikeViewSet,
    CommentViewSet,
    HashtagViewSet,
    HashtagGeneratorViewSet,
)

urlpatterns = [
    # General post endpoints
    path(
        "all/",
        PostViewSet.as_view({"get": "list"}),
        name="all-posts",
    ),
    path(
        "create/",
        PostViewSet.as_view({"post": "create"}),
        name="create-post",
    ),
    path(
        "<str:pk>/",
        PostViewSet.as_view({
            "get": "retrieve",
            "put": "update",
            "delete": "destroy"
        }),
        name="post-detail",
    ),

    # Feed endpoint (posts from followed users)
    path(
        "following/",
        SpecificPostViewSet.as_view({"get": "list"}),
        name="following-posts",
    ),

    # Like endpoints
    path(
        "<str:post_id>/like/",
        LikeViewSet.as_view({"post": "create", "delete": "destroy"}),
        name="post-like",
    ),

    # Comment endpoints
    path(
        "<str:post_id>/comments/",
        CommentViewSet.as_view({
            "get": "list",
            "post": "create"
        }),
        name="post-comments",
    ),
    path(
        "<str:post_id>/comments/<str:pk>/",
        CommentViewSet.as_view({
            "get": "retrieve",
            "put": "update",
            "delete": "destroy"
        }),
        name="comment-detail",
    ),

    # Hashtag endpoints
    path(
        "hashtags/",
        HashtagViewSet.as_view({"get": "list"}),
        name="hashtag-list",
    ),
    path(
        "hashtags/<str:pk>/",
        HashtagViewSet.as_view({"get": "retrieve"}),
        name="hashtag-posts",
    ),
    path(
        "hashtags/generate/",
        HashtagGeneratorViewSet.as_view({"post": "post"}),
        name="generate-hashtags",
    ),
] 
