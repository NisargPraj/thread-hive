from rest_framework import serializers
from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import Post, Like, Comment, Hashtag
from django.conf import settings
import os


class PostSerializer(DocumentSerializer):
    """
    Serializer for creating and retrieving posts.
    Handles validation for hashtags and optional image uploads.
    """

    hashtags = serializers.ListField(
        child=serializers.CharField(max_length=50), allow_empty=True, required=False
    )
    likes = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    image = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "username",
            "content",
            "image",
            "hashtags",
            "created_at",
            "updated_at",
            "likes",
            "comments_count",
        ]
        read_only_fields = ["created_at", "updated_at", "likes", "comments_count"]

    def get_likes(self, obj):
        """Get the number of likes for a post"""
        return Like.objects(post=obj).count()

    def get_comments_count(self, obj):
        """Get the number of comments for a post"""
        return Comment.objects(post=obj).count()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['timestamp'] = ret.pop('created_at')
        # Convert image to full URL if it exists
        if instance.image:
            # Get the filename from the GridFS storage
            filename = instance.image.filename
            if filename:
                # Construct the URL using the filename
                ret['image'] = f"http://localhost:8001{settings.MEDIA_URL}posts/{instance.username}/{filename}"
            else:
                ret['image'] = None
        return ret

    def validate_image(self, value):
        """
        Validate the image file.
        """
        if value:
            # Check file extension
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.gif']:
                raise serializers.ValidationError("Unsupported image format. Use JPEG, PNG or GIF.")
            
            # Check file size (max 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Image file too large. Size should not exceed 5MB.")
        return value

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
        
        # Create the post instance
        image_file = validated_data.pop('image', None)  # remove image from validated_data
        post = Post(**validated_data)  # create post without image

        if image_file:
            # now safely put the image once
            post.image.put(
                image_file,
                filename=f"{validated_data['username']}_{image_file.name}",
                content_type=image_file.content_type
            )

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

        # Handle image update
        if 'image' in validated_data:
            image_file = validated_data['image']
            if image_file:
                # Delete old image if it exists
                if instance.image:
                    instance.image.delete()
                
                # Set the filename to include username for organization
                filename = f"{instance.username}_{image_file.name}"
                instance.image.put(
                    image_file,
                    filename=filename,
                    content_type=image_file.content_type
                )
            elif instance.image:
                # If image is set to None, delete the existing image
                instance.image.delete()

        # Update other fields
        for attr, value in validated_data.items():
            if attr != 'image':  # Skip image as we handled it above
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
