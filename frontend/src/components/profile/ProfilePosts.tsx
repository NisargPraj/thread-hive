import Post from "../shared/Post";
import { useEffect, useState } from "react";

interface ProfilePostsProps {
  username: string;
}

interface PostType {
  id: string;
  username: string;
  content: string;
  timestamp: string;
  likes: number;
  comments_count: number;
  image?: string;
}

export const ProfilePosts: React.FC<ProfilePostsProps> = ({ username }) => {
  const [posts, setPosts] = useState<PostType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUserPosts = async () => {
      try {
        const response = await fetch(
          `http://54.208.64.57:8001/api/posts/posts/user/${username}/`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("access_token")}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error("Failed to fetch posts");
        }

        const data = await response.json();
        setPosts(data.results || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch posts");
      } finally {
        setLoading(false);
      }
    };

    fetchUserPosts();
  }, [username]);

  if (loading) {
    return <div className="flex justify-center p-4">Loading posts...</div>;
  }

  if (error) {
    return <div className="text-red-500 p-4">Error: {error}</div>;
  }

  if (posts.length === 0) {
    return <div className="text-gray-500 p-4">No posts yet.</div>;
  }

  return (
    <div className="space-y-4">
      {posts.map((post) => (
        <Post key={post.id} {...post} />
      ))}
    </div>
  );
};
