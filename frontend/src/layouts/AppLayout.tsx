// AppLayout.tsx
import React from "react";
import LeftSidebar from "@/components/LeftSidebar";
import MainContent from "@/components/MainContent";
import RightSidebar from "@/components/RightSidebar";

const AppLayout: React.FC = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-12 min-h-screen">
      <aside className="col-span-2 bg-gray-100 p-4 hidden md:block">
        <LeftSidebar />
      </aside>

      <main className="col-span-1 md:col-span-8 border-l border-r p-4">
        <MainContent />
      </main>

      <aside className="md:col-span-2 bg-gray-100 p-4 hidden lg:block">
        <RightSidebar />
      </aside>
    </div>
  );
};

export default AppLayout;
