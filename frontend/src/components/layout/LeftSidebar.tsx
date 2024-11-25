// components/LeftSidebar.tsx
import React from "react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

const LeftSidebar: React.FC = () => {
  return (
    <nav>
      <ul className="space-y-2">
        <li>
          <Link to="/">
            <Button variant="ghost">Home</Button>
          </Link>
        </li>
        <li>
          <Button variant="ghost">Explore</Button>
        </li>
        <li>
          <Button variant="ghost">Notifications</Button>
        </li>
        <li>
          <Button variant="ghost">Messages</Button>
        </li>
        <li>
          <Button variant="ghost">Bookmarks</Button>
        </li>
        <li>
          <Link to="/profile">
            <Button variant="ghost">Profile</Button>
          </Link>
        </li>
      </ul>
    </nav>
  );
};

export default LeftSidebar;
