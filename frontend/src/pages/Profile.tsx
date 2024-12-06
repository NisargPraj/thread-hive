import { ProfileHeader } from "@/components/profile/ProfileHeader";
import { ProfilePosts } from "@/components/profile/ProfilePosts";
import { ProfileStats } from "@/components/profile/ProfileStats";
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

const BASE_URL = "http://localhost:8000/api/users/";

interface UserProfile {
  username: string;
  handle: string;
  avatar_url: string;
  bio: string;
  following: number;
  followers: number;
  joined: string;
}

const Profile: React.FC = () => {
  const { username } = useParams();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<string | null>(null);

  const profileUrl = `${BASE_URL}profile/${username}/`;
  const currentUserUrl = `${BASE_URL}profile/`;

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

        const currentUserData = currentUserResponse.json();
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
        console.log("[DEBUG]: data burada: ", profileData);

        const transformedProfile: UserProfile = {
          username: profileData.username,
          handle: profileData.handle,
          avatar_url: profileData.avatar_url,
          bio: profileData.bio,
          following: profileData.following,
          followers: profileData.followers,
          joined: profileData.joined,
        };

        setProfile(transformedProfile);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [currentUserUrl, profileUrl]);

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
    <div className="flex flex-col gap-4">
      <ProfileHeader
        username={profile.username}
        handle={profile.handle}
        avatar={profile.avatar_url}
        bio={profile.bio}
      />
      <ProfileStats
        following={profile.following}
        followers={profile.followers}
        joined={profile.joined}
      />
      <div className="actions">
        {isCurrentUser ? (
          <div className="flex gap-2">
            <button className="btn-primary">Edit Profile</button>
            <button className="btn-secondary">Update Password</button>
          </div>
        ) : (
          <div className="flex gap-2">
            <button className="btn-primary">Follow</button>
            <button className="btn-secondary">Message</button>
          </div>
        )}
      </div>
      <ProfilePosts username={profile.username} />
    </div>
  );
};

export default Profile;
