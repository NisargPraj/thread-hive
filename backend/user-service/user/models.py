from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True)  # Adding Bio
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)  # Adding Profile Image
    blocked_users = models.ManyToManyField('self', blank=True, related_name='blocked_by', symmetrical=False)
    followers = models.ManyToManyField('self', blank=True, related_name='following', symmetrical=False)

    def __str__(self):
        return self.username

    # Utility methods for Followers
    def follow(self, user):
        """Follow another user"""
        if user != self:
            self.followers.add(user)

    def unfollow(self, user):
        """Unfollow another user"""
        if user in self.followers.all():
            self.followers.remove(user)

    def is_following(self, user):
        """Check if the user is following another user"""
        return self.followers.filter(id=user.id).exists()

    # Utility methods for Blocking
    def block(self, user):
        """Block another user"""
        if user != self:
            self.blocked_users.add(user)

    def unblock(self, user):
        """Unblock another user"""
        if user in self.blocked_users.all():
            self.blocked_users.remove(user)

    def is_blocked(self, user):
        """Check if the user has blocked another user"""
        return self.blocked_users.filter(id=user.id).exists()
