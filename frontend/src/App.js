import React, { Suspense, lazy } from "react";
import { Routes, Route } from "react-router-dom";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Home from "./pages/Home";
import About from "./pages/About";
import HowToGuide from "./pages/HowToGuide";
import { Header } from "./components/Header";
import { Footer } from "./components/Footer";
import "./index.css";

// Lazy-load only the heavy page
const Lineup = lazy(() => import("./pages/Lineup"));

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-grow mt-24 px-4">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route
            path="/lineup"
            element={
              <Suspense fallback={<div>Loading Lineup...</div>}>
                <Lineup />
              </Suspense>
            }
          />
          <Route path="/how-to-guide" element={<HowToGuide />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>

      <Footer />
    </div>
  );
}
