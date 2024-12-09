import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { Home, Search, Bell, Mail, Bookmark, User } from "lucide-react";

const BASE_URL = "http://localhost:8000/api/users/";

const LeftSidebar: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const currentUserUrl = `${BASE_URL}profile/`;

  useEffect(() => {
    const fetchCurrentUser = async () => {
      try {
        const token = localStorage.getItem("access_token");

        if (!token) {
          throw new Error("Not authenticated");
        }

        const currentUserResponse = await fetch(currentUserUrl, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!currentUserResponse.ok) {
          throw new Error("Failed to fetch current user");
        }

        const currentUserData = await currentUserResponse.json();

        setCurrentUser(currentUserData.username);
      } catch (err: any) {
        setError(err.message);
      }
    };
    fetchCurrentUser();
  }, [currentUserUrl]);

  return (
    <nav>
      <ul className="space-y-2">
        <li>
          <Link to="/home/">
            <Button variant="ghost">
              <Home size={20} className="mr-2" />
              Home
            </Button>
          </Link>
        </li>
        <li>
          <Button variant="ghost">
            <Search size={20} className="mr-2" />
            Explore
          </Button>
        </li>
        <li>
          <Button variant="ghost">
            <Bell size={20} className="mr-2" />
            Notifications
          </Button>
        </li>
        <li>
          <Button variant="ghost">
            <Mail size={20} className="mr-2" />
            Messages
          </Button>
        </li>
        <li>
          <Button variant="ghost">
            <Bookmark size={20} className="mr-2" />
            Bookmarks
          </Button>
        </li>
        <li>
          {currentUser ? (
            <Link to={`/profile/${currentUser}`}>
              <Button variant="ghost">
                <User size={20} className="mr-2" />
                My Profile
              </Button>
            </Link>
          ) : (
            <Button variant="ghost" disabled>
              <User size={20} className="mr-2" />
              Loading Profile...
            </Button>
          )}
        </li>
      </ul>
    </nav>
  );
};

export default LeftSidebar;
