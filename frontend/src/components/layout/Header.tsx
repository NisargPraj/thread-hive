// components/layout/Header.tsx
import React from "react";
import { Link } from "react-router-dom";
import { Home, User, Bell, Mail } from "lucide-react";

const Header: React.FC = () => {
  return (
    <header className="sticky top-0 z-50 bg-white border-b">
      <div className="flex items-center justify-between px-4 py-3">
        <Link to="/" className="text-xl font-bold">
          Social App
        </Link>
        <nav className="flex items-center space-x-4">
          <Link to="/" className="p-2 hover:bg-gray-100 rounded-full">
            <Home size={24} />
          </Link>
          <Link
            to="/notifications"
            className="p-2 hover:bg-gray-100 rounded-full"
          >
            <Bell size={24} />
          </Link>
          <Link to="/messages" className="p-2 hover:bg-gray-100 rounded-full">
            <Mail size={24} />
          </Link>
          <Link to="/profile" className="p-2 hover:bg-gray-100 rounded-full">
            <User size={24} />
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;
