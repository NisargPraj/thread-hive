import Post from "./Post";

const MainContent = () => {
  return (
    <div className="space-y-4">
      {/* We will map throught the posts here */}
      <Post />
    </div>
  );
};

export default MainContent;
