import { useEffect, useState } from "react";
import Post from "@/components/shared/Post";
import { Card } from "@/components/ui/card";

interface Post {
  id: string;
  content: string;
  timestamp: string; // Changed from created_at to timestamp
  image: string;
  username: string;
  likes: number;
  comments_count: number;
}

const Explore = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const response = await fetch(
          "http://54.208.64.57:8001/api/posts/posts/",
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
      } catch (error: unknown) {
        if (error instanceof Error) {
          setError(error.message);
        } else {
          setError("An unknown error occurred");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full">
        <p>Loading posts...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-full">
        <p className="text-red-500">Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4 p-4">
      <h1 className="text-2xl font-bold mb-6">Explore</h1>
      {posts.length === 0 ? (
        <Card className="p-4">
          <p className="text-center text-gray-500">No posts found</p>
        </Card>
      ) : (
        posts.map((post) => (
          <Post
            key={post.id}
            id={post.id}
            username={post.username}
            content={post.content}
            timestamp={post.timestamp} // Changed from created_at to timestamp
            likes={post.likes}
            comments_count={post.comments_count}
            image={post.image}
          />
        ))
      )}
    </div>
  );
};

export default Explore;
