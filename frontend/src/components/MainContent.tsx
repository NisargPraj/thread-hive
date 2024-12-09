import { useEffect, useState } from "react";
import Post from "./shared/Post";

interface PostData {
  id: string;
  username: string;
  content: string;
  timestamp: string;
  likes: number;
  comments_count: number;
  image: string;
}

interface ApiResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: PostData[];
}

interface MainContentProps {
  refreshTrigger?: boolean;
}

const MainContent: React.FC<MainContentProps> = ({ refreshTrigger }) => {
  const [posts, setPosts] = useState<PostData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPosts = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("access_token");
      const headers: HeadersInit = {
        Accept: "application/json",
      };

      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const response = await fetch(
        "http://localhost:8001/api/posts/following/",
        {
          headers,
        }
      );

      if (!response.ok) {
        throw new Error("Failed to fetch posts");
      }

      const data: ApiResponse = await response.json();
      console.log("data, ", data);
      setPosts(
        data.results.sort(
          (a, b) =>
            new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        )
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPosts();
  }, [refreshTrigger]); // Refetch when refreshTrigger changes

  if (loading) {
    return (
      <div className="flex justify-center items-center p-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-red-500 p-4 bg-red-50 rounded-lg">
        <p>Error: {error}</p>
        <button
          onClick={fetchPosts}
          className="mt-2 text-sm text-blue-500 hover:text-blue-600"
        >
          Try again
        </button>
      </div>
    );
  }

  if (posts.length === 0) {
    return (
      <div className="text-center text-gray-500 p-8 bg-gray-50 rounded-lg">
        <p className="text-lg">No posts yet.</p>
        <p className="text-sm mt-2">Be the first to share something!</p>
      </div>
    );
  }

  return (
    <div className="space-y-4 px-4">
      {posts.map((post) => (
        <Post
          key={post.id}
          id={post.id}
          username={post.username}
          content={post.content}
          timestamp={post.timestamp}
          likes={post.likes}
          comments_count={post.comments_count}
          image={post.image}
        />
      ))}
    </div>
  );
};

export default MainContent;
