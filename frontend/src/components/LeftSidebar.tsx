// components/LeftSidebar.tsx
import React from "react";
import { Button } from "@/components/ui/button";

const LeftSidebar: React.FC = () => {
  return (
    <nav>
      <ul className="space-y-2">
        <li>
          <Button variant="ghost" fullWidth>
            Home
          </Button>
        </li>
        <li>
          <Button variant="ghost" fullWidth>
            Explore
          </Button>
        </li>
        <li>
          <Button variant="ghost" fullWidth>
            Notifications
          </Button>
        </li>
        <li>
          <Button variant="ghost" fullWidth>
            Messages
          </Button>
        </li>
        <li>
          <Button variant="ghost" fullWidth>
            Bookmarks
          </Button>
        </li>
        <li>
          <Button variant="ghost" fullWidth>
            Profile
          </Button>
        </li>
      </ul>
    </nav>
  );
};

export default LeftSidebar;
