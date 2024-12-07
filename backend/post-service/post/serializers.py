from rest_framework import serializers
from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import Post, Like, Comment, Hashtag


class PostSerializer(DocumentSerializer):
    """
    Serializer for creating and retrieving posts.
    Handles validation for hashtags and optional image uploads.
    """

    hashtags = serializers.ListField(
        child=serializers.CharField(max_length=50), allow_empty=True, required=False
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "username",
            "content",
            "images",
            "hashtags",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_hashtags(self, value):
        """
        Ensure hashtags start with '#' and contain only valid characters.
        """
        for tag in value:
            if not tag.startswith("#"):
                raise serializers.ValidationError(
                    f"Hashtag '{tag}' must start with '#'"
                )
            if not tag[1:].isalnum():
                raise serializers.ValidationError(
                    f"Hashtag '{tag}' contains invalid characters."
                )
        return value

    def create(self, validated_data):
        """
        Override to handle hashtag logic during post creation.
        """
        hashtags = validated_data.pop("hashtags", [])
        post = Post(**validated_data)
        post.save()

        # Process each hashtag
        for tag in hashtags:
            # Get or create hashtag
            hashtag = Hashtag.objects(tag=tag).first()
            if not hashtag:
                hashtag = Hashtag(tag=tag)
                hashtag.save()

            # Update hashtag with post reference
            hashtag.increment_count(post)

            # Add hashtag reference to post
            if hashtag not in post.hashtags:
                post.hashtags.append(hashtag)

        # Save post again if hashtags were added
        if hashtags:
            post.save()

        return post

    def update(self, instance, validated_data):
        """
        Override to handle hashtag logic during post update.
        """
        new_hashtags = validated_data.pop("hashtags", [])
        old_hashtags = [hashtag.tag for hashtag in instance.hashtags]

        # Handle removed hashtags
        for tag in old_hashtags:
            if tag not in new_hashtags:
                hashtag = Hashtag.objects(tag=tag).first()
                if hashtag:
                    hashtag.decrement_count(instance)
                    if hashtag in instance.hashtags:
                        instance.hashtags.remove(hashtag)

        # Handle new hashtags
        for tag in new_hashtags:
            if tag not in old_hashtags:
                hashtag = Hashtag.objects(tag=tag).first()
                if not hashtag:
                    hashtag = Hashtag(tag=tag)
                    hashtag.save()
                hashtag.increment_count(instance)
                if hashtag not in instance.hashtags:
                    instance.hashtags.append(hashtag)

        # Update the instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class LikeSerializer(DocumentSerializer):
    """
    Serializer for handling likes on posts.
    Ensures a user can like a post only once.
    """

    username = serializers.CharField(
        required=False
    )  # Make username optional since it's set in view

    class Meta:
        model = Like
        fields = ["id", "post", "username", "created_at"]
        read_only_fields = ["created_at"]

    def validate(self, attrs):
        """
        Check if the user has already liked the post.
        """
        post = attrs.get("post")
        username = attrs.get("username")

        if Like.objects(post=post, username=username).first():
            raise serializers.ValidationError("You have already liked this post.")
        return attrs


class CommentSerializer(DocumentSerializer):
    """
    Serializer for handling comments on posts.
    """

    username = serializers.CharField(
        required=False
    )  # Make username optional since it's set in view

    class Meta:
        model = Comment
        fields = ["id", "post", "username", "content", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def create(self, validated_data):
        """
        Override to handle comment creation.
        """
        comment = Comment(**validated_data)
        comment.save()
        return comment


class HashtagSerializer(DocumentSerializer):
    """
    Serializer for retrieving hashtag information.
    """

    posts = serializers.SerializerMethodField()

    class Meta:
        model = Hashtag
        fields = ["id", "tag", "count", "posts", "last_updated"]
        read_only_fields = ["id", "count", "posts", "last_updated"]

    def get_posts(self, obj):
        """
        Retrieve post IDs instead of full objects to avoid serialization loops.
        """
        return [str(post.id) for post in obj.posts]

    def to_representation(self, instance):
        """
        Customize the representation to include post IDs instead of full objects.
        """
        representation = super().to_representation(instance)
        representation["posts"] = [str(post.id) for post in instance.posts]
        return representation
