import os
import base64
import openai
import requests
from rest_framework_mongoengine.viewsets import ModelViewSet, GenericViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework import mixins, status
from rest_framework.permissions import AllowAny
from .models import Post, Like, Comment, Hashtag
from .serializers import (
    PostSerializer,
    LikeSerializer,
    CommentSerializer,
    HashtagSerializer,
)
from .permissions import IsAuthenticatedCustom


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class PostViewSet(ModelViewSet):
    """
    ViewSet for handling CRUD operations on posts.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedCustom]
    pagination_class = CustomPagination

    def get_permissions(self):
        """Allow unauthenticated access to list and retrieve"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        """Get all posts"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Create a new post"""
        data = request.data.copy()
        data["username"] = request.user
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def perform_create(self, serializer):
        serializer.save(username=self.request.user)


class SpecificPostViewSet(ModelViewSet):
    """
    ViewSet for handling posts from followed users.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedCustom]
    pagination_class = CustomPagination

    def get_queryset(self):
        """Filter posts to show only those from followed users"""
        auth_token = self.request.headers.get("Authorization")
        if not auth_token:
            return Post.objects.none()

        try:
            response = requests.get(
                "http://user-service:8000/api/users/followings/",
                headers={"Authorization": auth_token},
            )
            if response.status_code == 200:
                followings = response.json()
                return Post.objects.filter(username__in=followings)
            return Post.objects.none()
        except requests.RequestException:
            return Post.objects.none()

    def list(self, request, *args, **kwargs):
        """Get posts from followed users"""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LikeViewSet(ModelViewSet):
    """
    ViewSet for handling likes on posts.
    """
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticatedCustom]

    def create(self, request, *args, **kwargs):
        """Like a post"""
        post_id = kwargs.get('post_id')
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        data = {
            "post": post.id,
            "username": request.user
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Unlike a post"""
        post_id = kwargs.get('post_id')
        try:
            like = Like.objects.get(post=post_id, username=request.user)
            like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Like.DoesNotExist:
            return Response(
                {"error": "Like not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )


class CommentViewSet(ModelViewSet):
    """
    ViewSet for handling comments on posts.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedCustom]
    pagination_class = CustomPagination

    def get_permissions(self):
        """Allow unauthenticated access to list and retrieve"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        """Filter comments by post"""
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post=post_id)

    def list(self, request, *args, **kwargs):
        """Get all comments for a specific post"""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Create a comment on a post"""
        post_id = kwargs.get('post_id')
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        data = request.data.copy()
        data["post"] = post.id
        data["username"] = request.user
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class HashtagViewSet(ModelViewSet):
    """
    ViewSet for handling hashtags and their associated posts.
    """
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = []
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        """Get all hashtags"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Get posts for a specific hashtag"""
        tag = kwargs.get("pk")
        hashtag = Hashtag.objects(tag=tag).first()
        if not hashtag:
            return Response(
                {"error": f"Hashtag #{tag} not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        posts = hashtag.posts
        serializer = PostSerializer(posts, many=True)
        return Response({
            "hashtag": f"#{tag}",
            "posts": serializer.data
        })


class HashtagGeneratorViewSet(GenericViewSet):
    """
    ViewSet for generating hashtags using AI.
    """
    permission_classes = [IsAuthenticatedCustom]

    def _encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _generate_hashtags(self, text=None, image=None):
        """Generate hashtags using OpenAI"""
        openai.api_key = os.getenv("OPENAI_API_KEY")

        if text and not image:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a social media expert that generates relevant hashtags. Generate 3-5 relevant hashtags based on the content provided. Return only the hashtags as a comma-separated list, without the # symbol.",
                    },
                    {
                        "role": "user",
                        "content": f"Generate hashtags for this text: {text}",
                    },
                ],
            )
            hashtags = response.choices[0].message.content.strip().split(",")

        elif image:
            temp_path = "/tmp/temp_image.jpg"
            with open(temp_path, "wb+") as destination:
                for chunk in image.chunks():
                    destination.write(chunk)

            base64_image = self._encode_image(temp_path)

            messages = [
                {
                    "role": "system",
                    "content": "You are a social media expert that generates relevant hashtags. Generate 3-5 relevant hashtags based on the content provided. Return only the hashtags as a comma-separated list, without the # symbol.",
                }
            ]

            image_message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Generate hashtags for this image:"
                        + (f" and text: {text}" if text else ""),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
            messages.append(image_message)

            response = openai.chat.completions.create(
                model="gpt-4o-mini", messages=messages, max_tokens=100
            )

            hashtags = response.choices[0].message.content.strip().split(",")
            os.remove(temp_path)
        else:
            hashtags = []

        return [f"#{tag.strip()}" for tag in hashtags if tag.strip()]

    def post(self, request):
        """Generate hashtags based on text and/or image"""
        
        text = request.data.get("text")
        image = request.FILES.get("image")

        if not text and not image:
            return Response(
                {"error": "Please provide either text or an image"},
                status=status.HTTP_400_BAD_REQUEST
            )

        hashtags = self._generate_hashtags(text=text, image=image)
        return Response({"hashtags": hashtags})
