// components/layout/Header.tsx
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Home, User, Bell, Mail, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";

const BASE_URL = "http://54.208.64.57:8000/api/users/";

const Header: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const currentUserUrl = `${BASE_URL}profile/`;
  const logoutUrl = `${BASE_URL}logout/`;

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

  const handleLogout = async () => {
    try {
      const refreshToken = localStorage.getItem("refresh_token");
      if (!refreshToken) {
        throw new Error("No refresh token available");
      }

      const response = await fetch(logoutUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({ refresh: refreshToken }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to logout");
      }

      // Clear tokens from local storage
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");

      // Redirect to login page
      window.location.href = "/login";
    } catch (error: any) {
      console.error("Logout error:", error.message);
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-white border-b">
      <div className="flex items-center justify-between px-4 py-3">
        <Link to="/" className="text-xl font-bold">
          Thread Hive
        </Link>
        <nav className="flex items-center space-x-4">
          <Link to="/home/" className="p-2 hover:bg-gray-100 rounded-full">
            <Home size={24} />
          </Link>
          <Link
            to="#"
            className="p-2 rounded-full text-gray-400 cursor-not-allowed pointer-events-none"
            aria-disabled="true"
          >
            <Bell size={24} />
          </Link>

          <Link
            to="#"
            className="p-2 rounded-full text-gray-400 cursor-not-allowed pointer-events-none"
            aria-disabled="true"
          >
            <Mail size={24} />
          </Link>
          <Link
            to={`/profile/${currentUser}`}
            className="p-2 hover:bg-gray-100 rounded-full"
          >
            <User size={24} />
          </Link>
          <Button
            variant="ghost"
            onClick={handleLogout}
            className="flex items-center gap-2 px-3 py-2 rounded-full bg-transparent hover:bg-gray-100"
          >
            <LogOut size={18} className="text-black" />
          </Button>
        </nav>
      </div>
    </header>
  );
};

export default Header;
