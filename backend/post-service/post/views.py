import os
import base64
import openai
import requests
from rest_framework_mongoengine.viewsets import ModelViewSet, GenericViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework import mixins
from .models import Post, Like, Comment, Hashtag
from .serializers import (
    PostSerializer,
    LikeSerializer,
    CommentSerializer,
    HashtagSerializer,
)
from .permissions import IsAuthenticatedCustom


class CustomPagination(PageNumberPagination):
    page_size = 10  # Default records per page
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

    def create(self, request, *args, **kwargs):
        """
        Create a new post with hashtags.
        Expected request data:
        {
            "content": "Post content here",
            "hashtags": ["#tag1", "#tag2"],
            "images": [optional_images]
        }
        """
        # Add username to request data
        data = request.data.copy()
        data["username"] = request.user

        # Create serializer with all data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def perform_create(self, serializer):
        """
        Save the post with the authenticated user's username.
        The serializer will handle hashtag creation and association.
        """
        serializer.save(username=self.request.user)


class SpecificPostViewSet(ModelViewSet):
    """
    ViewSet for handling CRUD operations on posts from followed users.
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedCustom]
    pagination_class = CustomPagination

    def get_queryset(self):
        """
        Filter posts to only show those from users the current user follows.
        """
        # Get the current user's auth token from the request
        auth_token = self.request.headers.get("Authorization")
        if not auth_token:
            return Post.objects.none()

        # Make request to user-service to get followings
        try:
            response = requests.get(
                "http://user-service:8000/api/users/followings/",
                headers={"Authorization": auth_token},
            )
            if response.status_code == 200:
                followings = response.json()
                # Filter posts to only include those from users we follow
                return Post.objects.filter(username__in=followings)
            return Post.objects.none()
        except requests.RequestException:
            return Post.objects.none()

    def list(self, request, *args, **kwargs):
        """
        Fetch posts from followed users with pagination.
        """
        queryset = self.get_queryset()
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

    def create(self, request, *args, **kwargs):
        """
        Create a new like with the authenticated user's username.
        """
        data = request.data.copy()
        data["username"] = request.user
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def perform_create(self, serializer):
        """
        Ensure a user can like a post only once.
        """
        post = serializer.validated_data["post"]
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

    def create(self, request, *args, **kwargs):
        """
        Create a new comment with the authenticated user's username.
        """
        data = request.data.copy()
        data["username"] = request.user
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

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
        tag = kwargs.get("pk")
        hashtag = Hashtag.objects(tag=tag).first()
        if not hashtag:
            return Response({"error": f"Hashtag #{tag} not found."}, status=404)

        posts = hashtag.posts
        serializer = PostSerializer(posts, many=True)
        return Response({"hashtag": f"#{tag}", "posts": serializer.data}, status=200)


class HashtagGeneratorViewSet(GenericViewSet):
    """
    ViewSet for generating hashtags using AI.
    """

    permission_classes = [IsAuthenticatedCustom]

    def _encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _generate_hashtags(self, text=None, image=None):
        """
        Generate hashtags using OpenAI based on text and/or image.
        """
        openai.api_key = os.getenv("OPENAI_API_KEY")

        if text and not image:
            # Text-only prompt
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
            # Save the uploaded image temporarily
            temp_path = "/tmp/temp_image.jpg"
            with open(temp_path, "wb+") as destination:
                for chunk in image.chunks():
                    destination.write(chunk)

            # Encode the image
            base64_image = self._encode_image(temp_path)

            # Create messages for the API call
            messages = [
                {
                    "role": "system",
                    "content": "You are a social media expert that generates relevant hashtags. Generate 3-5 relevant hashtags based on the content provided. Return only the hashtags as a comma-separated list, without the # symbol.",
                }
            ]

            # Add image content
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

            # Make the API call
            response = openai.chat.completions.create(
                model="gpt-4o-mini", messages=messages, max_tokens=100
            )

            hashtags = response.choices[0].message.content.strip().split(",")

            # Clean up temporary file
            os.remove(temp_path)
        else:
            hashtags = []

        # Clean up hashtags and add # prefix
        hashtags = [f"#{tag.strip()}" for tag in hashtags if tag.strip()]
        return hashtags

    @action(detail=False, methods=["post"])
    def generate(self, request):
        """
        Generate hashtags based on provided text and/or image.
        Returns hashtags with # prefix for frontend display.
        """
        text = request.data.get("text")
        image = request.FILES.get("image")

        if not text and not image:
            return Response(
                {"error": "Please provide either text or an image"}, status=400
            )

        hashtags = self._generate_hashtags(text=text, image=image)
        return Response({"hashtags": hashtags})
