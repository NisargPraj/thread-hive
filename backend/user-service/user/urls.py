from django.urls import path
from .views import (
    SignupView,
    LoginView,
    UserProfileView,
    UpdateProfileView,
    FollowUserView,
    UnfollowUserView,
    BlockUserView,
    UnblockUserView,
    BlockedListView,
    FollowingListView,
    FollowersListView
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update_profile'),
    path('profile/<str:username>/', UserProfileView.as_view(), name='view_user_profile'),
    path('follow/<str:username>/', FollowUserView.as_view(), name='follow_user'),
    path('unfollow/<str:username>/', UnfollowUserView.as_view(), name='unfollow_user'),
    path('block/<str:username>/', BlockUserView.as_view(), name='block_user'),
    path('unblock/<str:username>/', UnblockUserView.as_view(), name='unblock_user'),
    path('blocked-list/', BlockedListView.as_view(), name='blocked_list'),
    path('following/', FollowingListView.as_view(), name='following_list'),
    path('followers/', FollowersListView.as_view(), name='followers_list'),
]
