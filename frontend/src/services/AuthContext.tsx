import React, { createContext, useContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

interface AuthContextType {
  user: string | null;
  loading: boolean;
  login: (username: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const navigate = useNavigate();

  // API base for auth endpoints. REACT_APP_API_BASE should be the base URL
  // (e.g., "https://backend.onrender.com/api/v1"), and we append /auth here.
  const API_BASE =
    process.env.REACT_APP_API_BASE || "http://127.0.0.1:8000/api/v1";
  const AUTH_BASE = `${API_BASE}/auth`;

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

    if (refresh) {
      try {
        await fetch(`${AUTH_BASE}/logout/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access")}`,
          },
          body: JSON.stringify({ refresh }),
        });
      } catch (err) {
        console.error("Logout API error:", err);
      }
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