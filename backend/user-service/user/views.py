from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from .models import CustomUser
from .serializers import (
    UserSignupSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UpdateProfileSerializer,
    FollowSerializer,
)
from django.contrib.auth.models import User
from .utils.neo4j_conn import neo4j_connection


class SignupView(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data["username"],
                password=serializer.validated_data["password"],
            )
            if user:
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                        "message": "Login successful",
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.data)
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Successfully logged out"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username=None):
        if username:
            try:
                user = get_object_or_404(CustomUser, username=username)
                serializer = UserProfileSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UpdateProfileSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Profile updated successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        try:
            user_to_follow = get_object_or_404(CustomUser, username=username)

            query_check_block = """
                MATCH (u1:User {id: $user1_id})-[rel:BLOCK]->(u2:User {id: $user2_id})
                RETURN rel
            """

            blocked_by_you = neo4j_connection.query(
                query_check_block,
                parameters={"user1_id": request.user.id, "user2_id": user_to_follow.id},
            )
            blocked_by_them = neo4j_connection.query(
                query_check_block,
                parameters={"user1_id": user_to_follow.id, "user2_id": request.user.id},
            )

            # If a block exists, return an error response
            if blocked_by_you or blocked_by_them:
                return Response(
                    {"error": "Follow action not allowed due to block relationship."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            query_check = """
                MATCH (u1:User {id: $follower_id})-[r:FOLLOW]->(u2:User {id: $followee_id})
                RETURN r
            """
            existing_relation = neo4j_connection.query(
                query_check,
                parameters={
                    "follower_id": request.user.id,
                    "followee_id": user_to_follow.id,
                },
            )

            if existing_relation:
                return Response(
                    {"message": f"You are already following {user_to_follow.username}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            query = """
                MATCH (u1:User {id: $follower_id}), (u2:User {id: $followee_id})
                CREATE (u1)-[:FOLLOW]->(u2)
            """

            neo4j_connection.query(
                query,
                parameters={
                    "follower_id": request.user.id,
                    "followee_id": user_to_follow.id,
                },
            )

            return Response(
                {"message": f"You are now following {user_to_follow.username}"},
                status=status.HTTP_200_OK,
            )

        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UnfollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        try:
            user_to_unfollow = get_object_or_404(CustomUser, username=username)

            query = """
                MATCH (u1:User {id: $follower_id})-[r:FOLLOW]->(u2:User {id: $followee_id})
                DELETE r
            """

            neo4j_connection.query(
                query,
                parameters={
                    "follower_id": request.user.id,
                    "followee_id": user_to_unfollow.id,
                },
            )

            request.user.following.remove(user_to_unfollow)
            return Response(
                {"message": f"You unfollowed {user_to_unfollow.username}"},
                status=status.HTTP_200_OK,
            )
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class BlockUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        try:
            user_to_block = get_object_or_404(CustomUser, id=username)

            query_check = """
                MATCH (u1:User {id: $blocker_id})-[rel:BLOCK]->(u2:User {id: $blocked_id})
                RETURN rel
            """

            result = neo4j_connection.query(
                query_check,
                parameters={
                    "blocker_id": request.user.id,
                    "blocked_id": user_to_block.id,
                },
            )

            if result:
                return Response(
                    {"message": f"You have already blocked {user_to_block.username}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            query_unfollow = """
                MATCH (u1:User {id: $user1_id})-[rel:FOLLOW]->(u2:User {id: $user2_id})
                DELETE rel
            """
            # Unfollow from both sides
            neo4j_connection.query(
                query_unfollow,
                parameters={"user1_id": request.user.id, "user2_id": user_to_block.id},
            )
            neo4j_connection.query(
                query_unfollow,
                parameters={"user1_id": user_to_block.id, "user2_id": request.user.id},
            )

            # Add block relationship in Neo4j
            query = """
                MATCH (u1:User {id: $blocker_id}), (u2:User {id: $blocked_id})
                CREATE (u1)-[:BLOCK]->(u2)
            """

            neo4j_connection.query(
                query,
                parameters={
                    "blocker_id": request.user.id,
                    "blocked_id": user_to_block.id,
                },
            )

            return Response(
                {"message": f"You have blocked {user_to_block.username}"},
                status=status.HTTP_200_OK,
            )
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class UnblockUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        try:
            user_to_unblock = get_object_or_404(CustomUser, username=username)

            query_check = """
                MATCH (u1:User {id: $blocker_id})-[rel:BLOCK]->(u2:User {id: $blocked_id})
                RETURN rel
            """

            result = neo4j_connection.query(
                query_check,
                parameters={
                    "blocker_id": request.user.id,
                    "blocked_id": user_to_unblock.id,
                },
            )

            if not result:
                return Response(
                    {"message": f"{user_to_unblock.username} is not blocked"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Remove block relationship in Neo4j
            query = """
                MATCH (u1:User {id: $blocker_id})-[rel:BLOCK]->(u2:User {id: $blocked_id})
                DELETE rel
            """

            neo4j_connection.query(
                query,
                parameters={
                    "blocker_id": request.user.id,
                    "blocked_id": user_to_unblock.id,
                },
            )

            return Response(
                {"message": f"You have unblocked {user_to_unblock.username}"},
                status=status.HTTP_200_OK,
            )
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class BlockedListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = """
            MATCH (u1:User {id: $user_id})-[rel:BLOCK]->(u2:User)
            RETURN u2.id AS id, u2.username AS username, u2.first_name AS first_name, u2.last_name AS last_name
        """
        blocked_users = neo4j_connection.query(
            query, parameters={"user_id": request.user.id}
        )

        response = {"blocked_users": [dict(record) for record in blocked_users]}
        return Response(response, status=status.HTTP_200_OK)


class FollowingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username=None):
        user = get_object_or_404(CustomUser, username=username)

        query = """
            MATCH (u1:User {id: $user_id})-[:FOLLOW]->(u2:User)
            RETURN u2
        """
        results = neo4j_connection.query(query, parameters={"user_id": user.id})

        following_users = [
            {
                "id": record["u2"]["id"],
                "username": record["u2"]["username"],
                "first_name": record["u2"].get("first_name", ""),
                "last_name": record["u2"].get("last_name", ""),
                "profile_image": record["u2"].get("profile_image", ""),
            }
            for record in results
        ]

        return Response(following_users, status=status.HTTP_200_OK)


class FollowersListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username=None):
        user = get_object_or_404(CustomUser, username=username)
        query = """
            MATCH (u1:User)-[:FOLLOW]->(u2:User {id: $user_id})
            RETURN u1
        """
        results = neo4j_connection.query(query, parameters={"user_id": user.id})

        followers = [
            {
                "id": record["u1"]["id"],
                "username": record["u1"]["username"],
                "first_name": record["u1"].get("first_name", ""),
                "last_name": record["u1"].get("last_name", ""),
                "profile_image": record["u1"].get("profile_image", ""),
            }
            for record in results
        ]

        return Response(followers, status=status.HTTP_200_OK)


class HealthCheckView(APIView):
    """
    Health check endpoint for the user service
    """

    permission_classes = []

    def get(self, request):
        try:
            # Check database connection
            CustomUser.objects.first()

            # Check Neo4j connection by running a simple query
            query = "MATCH (n) RETURN n LIMIT 1"
            neo4j_connection.query(query)

            return Response(
                {
                    "status": "healthy",
                    "database": "connected",
                    "neo4j": "connected",
                }
            )
        except Exception as e:
            return Response(
                {"status": "unhealthy", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
