import React, { useEffect, useState } from "react";
import logo from "../assets/logo.png";
import { Button } from "../components/button";
import { useLocation, useNavigate } from "react-router-dom";

/**
 * Header Component
 * Displays the site logo, navigation menu, and auth actions.
 */
export function Header() {
  const location = useLocation(); // Get current route
  const navigate = useNavigate();

  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState<string | null>(null);

  // --- Base URL for your backend auth API ---
  const AUTH_BASE =
    process.env.REACT_APP_API_BASE || "http://127.0.0.1:8000/api/v1/auth";

  // --- Check login state on mount ---
  useEffect(() => {
    const token = localStorage.getItem("access");
    const storedUsername = localStorage.getItem("username");

    if (token && storedUsername) {
      setIsAuthenticated(true);
      setUsername(storedUsername);
    } else {
      setIsAuthenticated(false);
      setUsername(null);
    }
  }, [location]); // runs again when page changes

  // --- Handle Logout ---
  const handleLogout = async () => {
    const refresh = localStorage.getItem("refresh");
    if (!refresh) {
      localStorage.clear();
      setIsAuthenticated(false);
      navigate("/");
      return;
    }

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
      console.error("Logout error:", err);
    } finally {
      localStorage.clear();
      setIsAuthenticated(false);
      setUsername(null);
      navigate("/");
    }
  };

  // --- Main navigation links ---
  const navItems = [
    { id: "home", label: "Home", path: "/" },
    { id: "optimizer", label: "Lineup Optimizer", path: "/lineup" },
    { id: "guide", label: "How-to Guide", path: "/how-to-guide" },
    { id: "about", label: "About Us", path: "/about" },
  ];

  // Determine active nav/auth item based on current route
  const activeSection = navItems.find(
    (item) => item.path === location.pathname
  )?.id;

  return (
    <header className="border-b bg-card shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex h-20 items-center justify-between">
          {/* --- Logo --- */}
          <div className="flex items-center space-x-4 cursor-pointer" onClick={() => navigate("/")}>
            <img src={logo} alt="Bench Analytics" className="h-14 w-auto" />
          </div>

          {/* --- Desktop Navigation --- */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => (
              <Button
                key={item.id}
                variant={activeSection === item.id ? "default" : "ghost"}
                onClick={() => navigate(item.path)}
                className="px-4"
              >
                {item.label}
              </Button>
            ))}

            <span className="text-muted-foreground mx-2 select-none text-lg">|</span>

            {/* --- Authentication Actions --- */}
            <div className="flex items-center space-x-3">
              {isAuthenticated ? (
                <>
                  <span className="text-sm text-gray-700">
                    Logged in as <strong>{username}</strong>
                  </span>
                  <Button
                    onClick={handleLogout}
                    variant="outline"
                    className="ml-2 bg-red-600 text-white hover:bg-red-700"
                  >
                    Logout
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    variant="outline"
                    onClick={() => navigate("/login")}
                    className="bg-blue-600 text-white hover:bg-blue-700"
                  >
                    Login
                  </Button>
                  <Button
                    variant="default"
                    onClick={() => navigate("/register")}
                    className="bg-blue-700 text-white hover:bg-blue-800"
                  >
                    Register
                  </Button>
                </>
              )}
            </div>
          </nav>
        </div>
      </div>
    </header>
  );
}
