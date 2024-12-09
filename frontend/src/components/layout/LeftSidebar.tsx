import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import {
  Home,
  Search,
  Bell,
  Mail,
  Bookmark,
  User,
  LayoutDashboard,
} from "lucide-react";

const BASE_URL = "http://54.208.64.57:8000/api/users/";

const LeftSidebar: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<string | null>(null);
  const [isAdmin, setIsAdmin] = useState<boolean>(false);

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
        setIsAdmin(currentUserData.username == "admin" || false);
      } catch (error: unknown) {
        console.error(
          "Failed to fetch current user:",
          error instanceof Error ? error.message : "Unknown error"
        );
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
          <Link to="/explore">
            <Button variant="ghost">
              <Search size={20} className="mr-2" />
              Explore
            </Button>
          </Link>
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
        {isAdmin && (
          <li>
            <Link to="/admin">
              <Button variant="ghost">
                <LayoutDashboard size={20} className="mr-2" />
                Admin Dashboard
              </Button>
            </Link>
          </li>
        )}
      </ul>
    </nav>
  );
};

export default LeftSidebar;
