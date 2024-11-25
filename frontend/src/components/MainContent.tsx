import Post from "./shared/Post";
import { posts } from "@/constants/post";

const MainContent = () => {
  return (
    <div className="space-y-4">
      {posts.map((post) => (
        <Post
          key={post.id}
          username={post.username}
          avatar={post.avatar}
          content={post.content}
          timestamp={post.timestamp}
          comments={post.comments}
          retweets={post.retweets}
          likes={post.likes}
          images={post.images}
        />
      ))}
    </div>
  );
};

export default MainContent;
