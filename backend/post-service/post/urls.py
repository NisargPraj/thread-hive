from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PostViewSet,
    SpecificPostViewSet,
    LikeViewSet,
    CommentViewSet,
    HashtagViewSet,
    HashtagGeneratorViewSet,
    DummyViewSet,
    HealthCheckView,
)

router = DefaultRouter()

router.register(r"posts", PostViewSet, basename="post")
router.register(r"following", SpecificPostViewSet, basename="following-posts")
router.register(r"likes", LikeViewSet, basename="like")
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"hashtags", HashtagViewSet, basename="hashtag")
router.register(
    r"hashtags/generate", HashtagGeneratorViewSet, basename="generate-hashtags"
)
router.register(r"dummy", DummyViewSet, basename="dummy")

urlpatterns = [
    path("", include(router.urls)),
    path("health/", HealthCheckView.as_view(), name="health_check"),
]
