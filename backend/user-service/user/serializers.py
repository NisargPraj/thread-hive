from rest_framework import serializers
from django.contrib.auth.models import User, make_password
from .models import CustomUser
from .utils.neo4j_conn import neo4j_connection


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'bio', 'profile_image']

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.first_name = validated_data.get('first_name', '')
        user.last_name = validated_data.get('last_name', '')
        user.bio = validated_data.get('bio', '')
        user.profile_image = validated_data.get('profile_image', None)
        user.save()

        query = """
            MERGE (u:User {id: $user_id})
            SET u.username = $username, u.first_name = $first_name, u.last_name = $last_name
        """

        neo4j_connection.query(query, parameters={
            'user_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        })

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'bio', 'profile_image']


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'bio', 'profile_image']


class FollowSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
