import React from "react";
import Header from "@/components/layout/Header";
import LeftSidebar from "@/components/layout/LeftSidebar";
import RightSidebar from "@/components/layout/RightSidebar";
import { Outlet } from "react-router-dom";

const AppLayout: React.FC = () => {
  return (
    <div className="min-h-screen">
      <Header />
      <div className="grid grid-cols-1 md:grid-cols-12">
        <aside className="col-span-2 bg-gray-100 p-4 hidden md:block sticky top-16 h-screen">
          <LeftSidebar />
        </aside>
        <main className="col-span-1 md:col-span-8 border-l border-r p-4">
          <Outlet />
        </main>
        <aside className="md:col-span-2 bg-gray-100 p-4 hidden lg:block sticky top-16 h-screen">
          <RightSidebar />
        </aside>
      </div>
    </div>
  );
};

export default AppLayout;
