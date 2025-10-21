import React from "react";
import { useState } from "react"
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Home from "./pages/Home";
import Lineup from "./pages/Lineup";
import HowToGuide from "./pages/HowToGuide";
import About from "./pages/About";
import { Header } from "./components/Header";
import { Footer } from "./components/Footer";
import "./index.css";


export default function App() {
  const [activeSection, setActiveSection] = useState('home');
  
  const renderContent = () => {
    switch (activeSection) {
        case 'home':
          return <Home setActiveSection={setActiveSection} />
        case 'optimizer':
          return <Lineup />
        case 'guide':
          return <HowToGuide />
        case 'about':
          return <About />
        default:
          return <Home setActiveSection={setActiveSection} />
      }
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header always visible */}
      <Header />

      {/* Test content */}

      {/* Main content with spacing so it appears below the header */}
      <main className="mt-24 px-4">
        <Routes>
          <Route path="/" element={<Home setActiveSection={setActiveSection} />} />
          <Route path="/login" element={<Login />} /> 
          <Route path="/lineup" element={<Lineup />} />
          <Route path="/how-to-guide" element={<HowToGuide />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}