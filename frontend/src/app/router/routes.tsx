import React, { Suspense, lazy } from "react";
import { Routes, Route } from "react-router-dom";

import Home from "presentation/pages/Home";
import Login from "presentation/pages/Login";
import Register from "presentation/pages/Register";
import About from "presentation/pages/About";
import HowToGuide from "presentation/pages/HowToGuide";

const Lineup = lazy(() => import("presentation/pages/LineupOptimizer").then((m) => ({ default: m.LineupOptimizer })));

const AppRoutes: React.FC = () => {
  return (
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
  );
};

export default AppRoutes;
