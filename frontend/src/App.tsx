import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Lineup from "./pages/Lineup";
import { Header } from "./components/Header";

function App() {
  return (
    <BrowserRouter>
      {/* Header always visible */}
      <Header />
      <h1>Hello React!</h1>
      {/* Main content with spacing so it appears below the header */}
      <main className="mt-24 px-4">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/lineup" element={<Lineup />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default App;