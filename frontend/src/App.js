import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Lineup from "./pages/Lineup";
import { Header } from "./components/Header";

export default function App() {
  return (
    <div>
      {/* Header always visible */}
      <Header />

      {/* Test content */}

      {/* Main content with spacing so it appears below the header */}
      <main className="mt-24 px-4">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/lineup" element={<Lineup />} />
        </Routes>
      </main>
    </div>
  );
}
