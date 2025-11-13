import React, { Suspense, lazy } from "react";
import { Routes, Route } from "react-router-dom";

import Home from "presentation/pages/HomePage";
import Login from "presentation/pages/LoginPage";
import Register from "presentation/pages/RegisterPage";
import About from "presentation/pages/AboutPage";
import HowToGuide from "presentation/pages/HowToGuidePage";

import ProtectedRoute from "../../services/ProtectedRoute";
import PublicRoute from "../../services/PublicRoute";

const Lineup = lazy(() =>
  import("presentation/pages/LineupOptimizerPage").then((m) => ({
    default: m.LineupOptimizer,
  }))
);

/**
 * AppRoutes
 *
 * - Defines all client-side routes for the application.
 * - Supports code-splitting via React.lazy and Suspense for heavy pages.
 * - Maps each path to its corresponding page component.
 */
const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        }
      />

      {/* Protected routes */}
      <Route
        path="/lineup"
        element={
          <ProtectedRoute>
            <Suspense fallback={<div>Loading Lineup...</div>}>
              <Lineup />
            </Suspense>
          </ProtectedRoute>
        }
      />

      {/* Always accessible */}
      <Route path="/" element={<Home />} />
      <Route path="/how-to-guide" element={<HowToGuide />} />
      <Route path="/about" element={<About />} />
    </Routes>
  );
};

export default AppRoutes;
