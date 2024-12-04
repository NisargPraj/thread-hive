from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, LikeViewSet, CommentViewSet, HashtagViewSet

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'likes', LikeViewSet, basename='like')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'hashtags', HashtagViewSet, basename='hashtag')

# Include the router's URLs
urlpatterns = [
    path('', include(router.urls)),  # Includes all the routes from the router
]
