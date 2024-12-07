import Post from "@/components/shared/Post";
import { posts } from "@/constants/post";

interface ProfilePostsProps {
  username: string;
}

export const ProfilePosts: React.FC<ProfilePostsProps> = ({ username }) => {
  const userPosts = posts.filter((post) => post.username === username); // get all user posts by username

  return (
    <div className="space-y-4">
      {userPosts.map((post) => (
        <Post key={post.id} {...post} />
      ))}
    </div>
  );
};
