import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import AppLayout from "@/layouts/AppLayout";
import Profile from "@/pages/Profile";
import Home from "@/pages/Home";
import Login from "@/pages/Login";
import Register from "@/pages/Register";

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route element={<AppLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/profile/:username" element={<Profile />} />
        </Route>
      </Routes>
    </Router>
  );
};

export default App;
