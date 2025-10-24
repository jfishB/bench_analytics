import React from "react";
import { Routes, Route } from "react-router-dom";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Home from "./pages/Home";
import Lineup from "./pages/Lineup";
import HowToGuide from "./pages/HowToGuide";
import About from "./pages/About";
import { Header } from "./components/Header";
import { Footer } from "./components/Footer";
import "./index.css";

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header always visible */}
      <Header />

      {/* Main content */}
      <main className="flex-grow mt-24 px-4">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route path="/lineup" element={<Lineup />} />
          <Route path="/how-to-guide" element={<HowToGuide />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>

      {/* Footer always visible */}
      <Footer />
    </div>
  );
}
