import React, { createContext, useContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "./authService";

interface AuthContextType {
  user: string | null;
  loading: boolean;
  login: (username: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const navigate = useNavigate();

  // --- Initialize auth state on mount ---
  useEffect(() => {
    const init = () => {
      const storedAccess = localStorage.getItem("access");
      const storedUsername = localStorage.getItem("username");
      if (storedAccess && storedUsername) {
        setUser(storedUsername);
      } else {
        setUser(null);
      }
      setLoading(false);
    };
    init();
  }, []);

  // --- Login just stores username (after successful backend login) ---
  const login = (username: string) => {
    localStorage.setItem("username", username);
    setUser(username);
  };

  // --- Logout (handles API call, cleanup, and navigation) ---
  const logout = async () => {
    const refresh = localStorage.getItem("refresh");
    const access = localStorage.getItem("access");

    if (refresh && access) {
      await authService.logout(refresh, access);
    }

    // Clear all auth data
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    localStorage.removeItem("username");
    setUser(null);

    // Navigate home
    navigate("/");
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook for easier access
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
