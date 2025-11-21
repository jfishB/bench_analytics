import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../services/AuthContext";

/**
 * PublicRoute
 *
 * - Defines interface that prevents logged in users from accessing pages they shouldn't.
 * - Ex: login/register pages when already authenticated.
 */

interface PublicRouteProps {
  children: React.ReactNode;
}

const PublicRoute: React.FC<PublicRouteProps> = ({ children }) => {
  const { user, loading } = useAuth();

  // wait until auth state is resolved before deciding
  if (loading) return null; // or a spinner component

  if (user) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default PublicRoute;