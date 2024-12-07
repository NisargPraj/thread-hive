interface ProfileStatsProps {
  following: number;
  followers: number;
}

export const ProfileStats: React.FC<ProfileStatsProps> = ({
  following,
  followers,
}) => {
  return (
    <div className="flex gap-4 p-4 border-b">
      <div>
        <span className="font-bold">{following}</span>
        <span className="text-gray-600 ml-1">Following</span>
      </div>
      <div>
        <span className="font-bold">{followers}</span>
        <span className="text-gray-600 ml-1">Followers</span>
      </div>
    </div>
  );
};
