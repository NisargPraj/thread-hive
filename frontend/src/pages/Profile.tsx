import { ProfilePosts } from "@/components/profile/ProfilePosts";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { UserPlus, User, UserMinus } from "lucide-react";

const BASE_URL = "http://localhost:8000/api/users/";

interface UserProfile {
  username: string;
  avatar_url: string;
  bio: string;
  following: number;
  followers: number;
}

const Profile: React.FC = () => {
  const { username } = useParams();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [followersCount, setFollowersCount] = useState<number>(0);
  const [followingCount, setFollowingCount] = useState<number>(0);
  const [currentUser, setCurrentUser] = useState<string | null>(null);
  const [isFollowing, setIsFollowing] = useState<boolean>(false);

  const profileUrl = `${BASE_URL}profile/${username}/`;
  const currentUserUrl = `${BASE_URL}profile/`;
  const followersUrl = `${BASE_URL}followers/${username}/`;
  const followingUrl = `${BASE_URL}following/${username}/`;

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem("access_token");

        if (!token) {
          throw new Error("Not authenticated");
        }

        const currentUserResponse = await fetch(currentUserUrl, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!currentUserResponse.ok) {
          throw new Error("Failed to fetch current user");
        }

        const currentUserData = await currentUserResponse.json();
        setCurrentUser(currentUserData.username);

        const profileResponse = await fetch(profileUrl, {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });
        if (!profileResponse.ok) {
          throw new Error(`Failed to fetch profile: ${profileResponse.status}`);
        }

        const profileData = await profileResponse.json();

        const transformedProfile: UserProfile = {
          username: profileData.username,
          avatar_url: profileData.profile_image,
          bio: profileData.bio,
          following: profileData.following,
          followers: profileData.followers,
        };

        setProfile(transformedProfile);

        const followersResponse = await fetch(followersUrl, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (followersResponse.ok) {
          const followersData = await followersResponse.json();

          setFollowersCount(followersData.length);
          setIsFollowing(
            followersData.some(
              (follower: any) => follower.username === currentUserData.username
            )
          );
        }

        // Fetch following count
        const followingResponse = await fetch(followingUrl, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (followingResponse.ok) {
          const followingData = await followingResponse.json();
          setFollowingCount(followingData.length);
        }
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [currentUserUrl, profileUrl, followersUrl, followingUrl]);

  const handleFollow = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        throw new Error("Not authenticated");
      }

      const followUrl = `${BASE_URL}follow/${profile?.username}/`;

      const response = await fetch(followUrl, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to follow user: ${response.statusText}`);
      }

      setIsFollowing(true);
      setFollowersCount((prev) => prev + 1);
    } catch (error: any) {
      console.error("Error following user:", error.message);
    }
  };

  const handleUnfollow = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        throw new Error("Not authenticated");
      }

      const unfollowUrl = `${BASE_URL}unfollow/${profile?.username}/`;

      const response = await fetch(unfollowUrl, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to unfollow user: ${response.statusText}`);
      }

      setIsFollowing(false);
      setFollowersCount((prev) => prev - 1);
    } catch (error: any) {
      console.error("Error unfollowing user:", error.message);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center">Loading...</div>;
  }

  if (error) {
    return (
      <div className="text-red-500 flex items-center justify-center">
        Error: {error}
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="flex items-center justify-center">
        No profile data available.
      </div>
    );
  }

  const isCurrentUser: boolean = profile.username === currentUser;

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="relative">
        {/* Cover Photo Placeholder */}
        <div className="h-40 bg-gray-200 rounded-t-lg"></div>

        {/* Profile Picture */}
        <Avatar className="w-32 h-32 absolute -bottom-16 left-4 border-4 border-white">
          <AvatarImage src={profile.avatar_url || ""} alt={profile.username} />
          <AvatarFallback>
            <User className="w-12 h-12 text-gray-500" />
          </AvatarFallback>
        </Avatar>

        {/* Follow Button */}
        <div className="absolute top-4 right-4">
          {!isCurrentUser &&
            (isFollowing ? (
              <Button variant="secondary" onClick={handleUnfollow}>
                <UserMinus className="mr-2 h-5 w-5" /> Unfollow
              </Button>
            ) : (
              <Button variant="default" onClick={handleFollow}>
                <UserPlus className="mr-2 h-5 w-5" /> Follow
              </Button>
            ))}
        </div>
      </div>

      <div className="mt-16 p-4">
        {/* Profile Name and Username */}
        <h1 className="text-2xl font-bold">{profile.username}</h1>
        <p className="text-gray-500">@{profile.username}</p>

        {/* Bio */}
        <p className="mt-2">{profile.bio}</p>

        {/* Profile Stats */}
        <div className="flex gap-4 mt-4">
          <div>
            <span className="font-bold">{followersCount}</span> Followers
          </div>
          <div>
            <span className="font-bold">{followingCount}</span> Following
          </div>
        </div>

        {/* Tab Navigation */}
        <Tabs defaultValue="posts" className="mt-6 w-full">
          <TabsList className="grid grid-cols-3 w-full">
            <TabsTrigger value="posts" className="w-full">
              Posts
            </TabsTrigger>
            <TabsTrigger value="replies" className="w-full">
              Replies
            </TabsTrigger>
            <TabsTrigger value="media" className="w-full">
              Media
            </TabsTrigger>
          </TabsList>

          <TabsContent value="posts">
            <ProfilePosts username={profile.username} />
          </TabsContent>
          <TabsContent value="replies">
            <div>Replies content coming soon...</div>
          </TabsContent>
          <TabsContent value="media">
            <div>Media content coming soon...</div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Profile;
