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
from rest_framework.views import APIView
from .models import Post, Like, Comment, Hashtag
from .serializers import (
    PostSerializer,
    LikeSerializer,
    CommentSerializer,
    HashtagSerializer,
)
from .permissions import IsAuthenticatedCustom
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class DummyViewSet(ModelViewSet):
    def list(self, request):
        return Response("Dummy Response")


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
        if self.action in ["list", "retrieve", "by_user"]:
            return [AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=["get"], url_path="user/(?P<username>[^/.]+)")
    def by_user(self, request, username=None):
        try:
            posts = Post.objects.filter(username=username)
            page = self.paginate_queryset(posts)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(posts, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve posts from user {username}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

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
        try:
            # Log the incoming request data
            logger.debug(f"Request data: {request.data}")
            logger.debug(f"Request FILES: {request.FILES}")

            # Create a mutable copy of the data
            data = {}
            for key, value in request.data.items():
                if key == "hashtags":
                    # Convert hashtags to a list if it's not already
                    if isinstance(value, str):
                        data[key] = [value]
                    elif isinstance(value, (list, tuple)):
                        data[key] = value
                    else:
                        data[key] = []
                elif key != "image":  # Skip the image file
                    data[key] = value

            # Add the username
            data["username"] = request.user

            # If there's an image file, add it separately
            if "image" in request.FILES:
                logger.debug(f"Image file found: {request.FILES['image'].name}")
                data["image"] = request.FILES["image"]

            # Log the data being passed to serializer
            logger.debug(f"Data being passed to serializer: {data}")

            serializer = self.get_serializer(data=data)

            # Log validation errors if any
            if not serializer.is_valid():
                logger.error(f"Serializer validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=201, headers=headers)
        except Exception as e:
            logger.error(f"Error creating post: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        try:
            serializer.save(username=self.request.user)
        except Exception as e:
            logger.error(f"Error in perform_create: {str(e)}")
            raise


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
        logger.debug(f"Access token: {auth_token}")  # Fixed f-string syntax
        if not auth_token:
            return Post.objects.none()

        try:
            # Get the authenticated user's username
            username = str(self.request.user)

            # Call the user service with the correct endpoint including username
            response = requests.get(
                f"http://user-service:8000/api/users/following/{username}/",
                headers={"Authorization": auth_token},
            )
            if response.status_code == 200:
                # Extract usernames from the following users list
                following_users = [user["username"] for user in response.json()]
                return Post.objects.filter(username__in=following_users)
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

    @action(detail=True, methods=["get"], url_path="check")
    def check(self, request, id=None):
        """Check if a user has liked a post"""
        try:
            post = Post.objects.get(id=id)
            like = Like.objects.filter(post=post, username=request.user).first()
            return Response({"liked": bool(like)})
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error checking like status: {str(e)}")
            return Response(
                {"error": "Failed to check like status"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def like(self, request, id=None):
        """Like a post"""
        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )

        data = {"post": post.id, "username": request.user}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"])
    def unlike(self, request, id=None):
        """Unlike a post"""

        try:
            like = Like.objects.get(post=id, username=request.user)
            like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Like.DoesNotExist:
            return Response(
                {"error": "Like not found"}, status=status.HTTP_404_NOT_FOUND
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
        if self.action in ["list", "retrieve", "list_comments"]:
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        """Filter comments by post"""
        post_id = self.kwargs.get("post_id")
        return Comment.objects.filter(post=post_id)

    @action(detail=False, methods=["get"], url_path=r"by_post/(?P<post_id>[^/.]+)")
    def list_comments(self, request, post_id=None):
        """
        Retrieve all comments for a specific post by post ID.
        """
        comments = Comment.objects.filter(post=post_id)
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path=r"add/(?P<post_id>[^/.]+)")
    def create_comment(self, request, post_id=None):
        """
        Add a comment to a specific post by post ID.
        """
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Prepare the data for the serializer
        data = request.data.copy()
        data["post"] = post.id
        data["username"] = request.user

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"], url_path="delete")
    def delete_comment(self, request, pk=None):
        """
        Delete a comment. Only the comment creator can delete their own comments.
        """
        try:
            comment = Comment.objects.get(id=pk)

            # Check if the requesting user is the comment creator
            if str(comment.username) != str(request.user):
                return Response(
                    {"error": "You can only delete your own comments"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Comment.DoesNotExist:
            return Response(
                {"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error deleting comment: {str(e)}")
            return Response(
                {"error": "Failed to delete comment"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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
                status=status.HTTP_404_NOT_FOUND,
            )

        posts = hashtag.posts
        serializer = PostSerializer(posts, many=True)
        return Response({"hashtag": f"#{tag}", "posts": serializer.data})


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

    @action(detail=False, methods=["post"])
    def generate(self, request):
        """Generate hashtags based on text and/or image"""

        text = request.data.get("text")
        image = request.FILES.get("image")

        if not text and not image:
            return Response(
                {"error": "Please provide either text or an image"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        hashtags = self._generate_hashtags(text=text, image=image)
        return Response({"hashtags": hashtags})

    @action(detail=False, methods=["get"])
    def get_predefined_hashtags(self, request):
        hashtags = ["America", "USA", "TrumpWon", "ElonMusk", "Twitter"]
        return Response({"hashtags": hashtags})


class HealthCheckView(APIView):
    """
    Health check endpoint for the post service
    """

    permission_classes = []

    def get(self, request):
        try:
            # Check MongoDB connection by making a simple query
            Post.objects.first()

            return Response(
                {
                    "status": "healthy",
                    "database": "connected",
                }
            )
        except Exception as e:
            return Response(
                {"status": "unhealthy", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
