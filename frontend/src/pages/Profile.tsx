import { ProfileHeader } from "@/components/profile/ProfileHeader";
import { ProfilePosts } from "@/components/profile/ProfilePosts";
import { ProfileStats } from "@/components/profile/ProfileStats";

const Profile: React.FC = () => {
  const profile = {
    username: "Elon Musk",
    handle: "@elonmusk",
    avatar: "/images/avatar/elon_musk.jpg",
    bio: "Technoking of Tesla, Chief Twit at X",
    following: 180,
    followers: "128.9M",
    joined: "June 2009",
  };

  return (
    <div className="flex flex-col gap-4">
      <ProfileHeader {...profile} />
      <ProfileStats {...profile} />
      <ProfilePosts username={profile.username} />
    </div>
  );
};

export default Profile;
