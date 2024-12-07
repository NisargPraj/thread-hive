import { Avatar, AvatarImage } from "@/components/ui/avatar";

interface ProfileHeaderProps {
  username: string;
  avatar: string;
  bio: string;
}

export const ProfileHeader: React.FC<ProfileHeaderProps> = ({
  username,
  avatar,
  bio,
}) => {
  return (
    <div className="p-4 border-b">
      <div className="flex items-start gap-4">
        <Avatar className="w-32 h-32">
          <AvatarImage src={avatar} alt={username} />
        </Avatar>
        <div className="flex-1">
          <h1 className="text-xl font-bold">{username}</h1>
          <p className="mt-2">{bio}</p>
        </div>
      </div>
    </div>
  );
};
