import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../services/AuthContext";

/**
 * ProtectedRoute
 *
 * - Defines interface that prevents not authenticated users from accessing pages they shouldn't.
 * - Ex: lineup optimizer page.
 */

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;