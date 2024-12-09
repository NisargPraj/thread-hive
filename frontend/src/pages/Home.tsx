import React, { useState } from "react";
import MainContent from "../components/MainContent";
import CreatePost from "../components/shared/CreatePost";

const Home: React.FC = () => {
  const [refreshTrigger, setRefreshTrigger] = useState(false);

  const handlePostCreated = () => {
    // Toggle the refresh trigger to cause MainContent to refetch
    setRefreshTrigger((prev) => !prev);
  };

  return (
    <div className="space-y-4">
      <div className="border-b pb-4">
        <h1 className="text-xl font-bold px-4">Home</h1>
      </div>

      {/* Create Post Section */}
      <div className="px-4">
        <CreatePost onPostCreated={handlePostCreated} />
      </div>

      {/* Posts List */}
      <MainContent refreshTrigger={refreshTrigger} />
    </div>
  );
};

export default Home;
