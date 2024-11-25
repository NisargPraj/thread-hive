// pages/Home.tsx
import React from "react";
import Post from "@/components/shared/Post";
import { posts } from "@/constants/post";

const Home: React.FC = () => {
  return (
    <div className="space-y-4">
      <div className="border-b pb-4">
        <h1 className="text-xl font-bold px-4">Home</h1>
      </div>

      {/* Create Post Section */}
      <div className="p-4 border-b">
        <textarea
          className="w-full p-2 border rounded-lg resize-none"
          placeholder="What's happening?"
          rows={3}
        />
        <div className="flex justify-end mt-2">
          <button className="bg-blue-500 text-white px-4 py-2 rounded-full hover:bg-blue-600">
            Post
          </button>
        </div>
      </div>

      {/* Posts Feed */}
      <div className="space-y-4">
        {posts.map((post) => (
          <Post key={post.id} {...post} />
        ))}
      </div>
    </div>
  );
};

export default Home;
