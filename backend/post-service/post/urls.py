from django.urls import path
from .views import (
    PostViewSet,
    SpecificPostViewSet,
    LikeViewSet,
    CommentViewSet,
    HashtagViewSet,
    HashtagGeneratorViewSet,
)

urlpatterns = [
    # Post endpoints
    path(
        "posts/",
        PostViewSet.as_view({"get": "list", "post": "create"}),
        name="post-list",
    ),
    path(
        "posts/<str:pk>/",
        PostViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
        name="post-detail",
    ),
    # Feed endpoint (posts from followed users)
    path(
        "feed/",
        SpecificPostViewSet.as_view({"get": "list"}),
        name="feed-list",
    ),
    # Like endpoints
    path("likes/", LikeViewSet.as_view({"post": "create"}), name="like-create"),
    path(
        "likes/<str:pk>/",
        LikeViewSet.as_view({"delete": "destroy"}),
        name="like-delete",
    ),
    # Comment endpoints
    path(
        "comments/", CommentViewSet.as_view({"post": "create"}), name="comment-create"
    ),
    path(
        "comments/<str:pk>/",
        CommentViewSet.as_view({"delete": "destroy"}),
        name="comment-delete",
    ),
    # Hashtag endpoints
    path("hashtags/", HashtagViewSet.as_view({"get": "list"}), name="hashtag-list"),
    path(
        "hashtags/<str:pk>/",
        HashtagViewSet.as_view({"get": "retrieve"}),
        name="hashtag-detail",
    ),
    # Hashtag generator endpoint
    path(
        "hashtag-generator/generate/",
        HashtagGeneratorViewSet.as_view({"post": "generate"}),
        name="hashtag-generate",
    ),
]
