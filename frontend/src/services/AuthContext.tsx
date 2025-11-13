import React, { createContext, useContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

interface AuthContextType {
  user: string | null;
  login: (username: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<string | null>(null);
  const navigate = useNavigate();

  const AUTH_BASE =
    process.env.REACT_APP_API_BASE || "http://127.0.0.1:8000/api/v1/auth";

  // --- Initialize auth state on mount ---
  useEffect(() => {
    const storedAccess = localStorage.getItem("access");
    const storedUsername = localStorage.getItem("username");
    if (storedAccess && storedUsername) {
      setUser(storedUsername);
    }
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
    <AuthContext.Provider value={{ user, login, logout }}>
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