from rest_framework_mongoengine.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Post, Like, Comment, Hashtag
from .serializers import PostSerializer, LikeSerializer, CommentSerializer, HashtagSerializer
from .permissions import IsAuthenticatedCustom


class CustomPagination(PageNumberPagination):
    page_size = 10  # Default records per page
    page_size_query_param = 'page_size'
    max_page_size = 100


class PostViewSet(ModelViewSet):
    """
    ViewSet for handling CRUD operations on posts.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedCustom]
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        """
        Fetch all posts with pagination.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        Automatically assign the authenticated user's username to the post.
        """
        print(f"Authenticated user: {self.request.user}")
        serializer.save(username=self.request.user)


class LikeViewSet(ModelViewSet):
    """
    ViewSet for handling likes on posts.
    """
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticatedCustom]

    def perform_create(self, serializer):
        """
        Ensure a user can like a post only once.
        """
        post = serializer.validated_data['post']
        username = self.request.user

        if Like.objects(post=post.id, username=username).first():
            raise ValidationError("You have already liked this post.")
        serializer.save(username=username)


class CommentViewSet(ModelViewSet):
    """
    ViewSet for handling comments on posts.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedCustom]

    def perform_create(self, serializer):
        """
        Automatically assign the authenticated user's username to the comment.
        """
        serializer.save(username=self.request.user)


class HashtagViewSet(ModelViewSet):
    """
    ViewSet for handling hashtags and their associated posts.
    """
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = []  # No authentication required for hashtags

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve posts associated with a specific hashtag.
        """
        tag = kwargs.get('pk')
        hashtag = Hashtag.objects(tag=tag).first()
        if not hashtag:
            return Response({"error": f"Hashtag #{tag} not found."}, status=404)

        posts = hashtag.posts
        serializer = PostSerializer(posts, many=True)
        return Response({"hashtag": f"#{tag}", "posts": serializer.data}, status=200)
