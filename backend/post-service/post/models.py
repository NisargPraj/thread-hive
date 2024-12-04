from mongoengine import (
    Document,
    StringField,
    DateTimeField,
    ListField,
    FileField,
    IntField,
    ReferenceField,
)
from datetime import datetime


class Post(Document):
    """
    Represents a Post created by a user.
    Includes optional image uploads, timestamps, and associated hashtags.
    """
    username = StringField(required=True, max_length=150)  # User's username
    content = StringField(required=True, max_length=280)  # Post content (max 280 chars)
    created_at = DateTimeField(default=datetime.utcnow)  # Creation timestamp
    updated_at = DateTimeField(default=datetime.utcnow)  # Update timestamp
    images = ListField(FileField(), default=list)  # Optional list of uploaded images
    hashtags = ListField(ReferenceField('Hashtag'), default=list)  # References to associated Hashtag documents

    meta = {
        'collection': 'posts',  # MongoDB collection name
        'ordering': ['-created_at'],  # Default ordering by latest posts
        'indexes': ['created_at'],  # Index for efficient querying by timestamp
    }

    def save(self, *args, **kwargs):
        """Override save to update the `updated_at` timestamp."""
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return f"Post by {self.username}: {self.content[:20]}..."


class Like(Document):
    """
    Represents a Like on a post.
    Tracks which user liked a post and when.
    """
    post = ReferenceField('Post', required=True)  # Reference to the related Post document
    username = StringField(required=True, max_length=150)  # User who liked the post
    created_at = DateTimeField(default=datetime.utcnow)  # When the like was made

    meta = {
        'collection': 'likes',  # MongoDB collection name
        'ordering': ['-created_at'],  # Default ordering by latest likes
        'indexes': [
            {'fields': ('post', 'username'), 'unique': True},  # Ensure unique likes per user per post
        ],
    }

    def __str__(self):
        return f"Like by {self.username} on post {self.post.id}"


class Comment(Document):
    """
    Represents a Comment on a post.
    Tracks the post, user, and content of the comment.
    """
    post = ReferenceField('Post', required=True)  # Reference to the related Post document
    username = StringField(required=True, max_length=150)  # User who made the comment
    content = StringField(required=True, max_length=280)  # Comment content (max 280 chars)
    created_at = DateTimeField(default=datetime.utcnow)  # When the comment was made
    updated_at = DateTimeField(default=datetime.utcnow)  # When the comment was last updated

    meta = {
        'collection': 'comments',  # MongoDB collection name
        'ordering': ['-created_at'],  # Default ordering by latest comments
        'indexes': ['created_at'],  # Index for efficient querying by timestamp
    }

    def save(self, *args, **kwargs):
        """Override save to update the `updated_at` timestamp."""
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super(Comment, self).save(*args, **kwargs)

    def __str__(self):
        return f"Comment by {self.username} on post {self.post.id}: {self.content[:20]}..."


class Hashtag(Document):
    """
    Represents a Hashtag and tracks its usage frequency and associated posts.
    """
    tag = StringField(required=True, unique=True)  # Unique hashtag text (e.g., '#AI')
    count = IntField(default=0)  # Total number of posts associated with this hashtag
    posts = ListField(ReferenceField(Post), default=list)  # List of posts associated with this hashtag
    last_updated = DateTimeField(default=datetime.utcnow)  # Last update timestamp

    meta = {
        'collection': 'hashtags',  # MongoDB collection name
        'ordering': ['-count'],  # Default ordering by most used hashtags
        'indexes': ['tag'],  # Index for faster lookups
    }

    def save(self, *args, **kwargs):
        """Override save to update the `last_updated` timestamp."""
        self.last_updated = datetime.utcnow()
        return super(Hashtag, self).save(*args, **kwargs)

    def increment_count(self, post):
        """Increments the count when a post is associated with the hashtag."""
        if post not in self.posts:
            self.posts.append(post)
            self.count += 1
            self.last_updated = datetime.utcnow()
            self.save()

    def decrement_count(self, post):
        """Decrements the count when a post is disassociated with the hashtag."""
        if post in self.posts:
            self.posts.remove(post)
            if self.count > 0:
                self.count -= 1
            self.last_updated = datetime.utcnow()
            self.save()

    def __str__(self):
        return f"#{self.tag} (Used {self.count} times)"
