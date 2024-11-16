import React from "react";
import { Card } from "@/components/ui/card";

const Post: React.FC = () => {
  return (
    <Card>
      <div className="p-4">
        <h3 className="p-4">User Name</h3>
        <p>Post content will come here</p>
      </div>
    </Card>
  );
};

export default Post;
