import React from "react";
import logo from "../assets/logo.png";
import { Button } from "../components/button";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "services/AuthContext";

export function Header() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

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
          <div
            className="flex items-center space-x-4 cursor-pointer"
            onClick={() => navigate("/")}
          >
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

            <span className="text-muted-foreground mx-2 select-none text-lg">
              |
            </span>

            {/* --- Authentication Actions --- */}
            <div className="flex items-center space-x-3">
              {user ? (
                <>
                  <span className="text-sm text-gray-700">
                    Logged in as <strong>{user}</strong>
                  </span>
                  <Button
                    onClick={logout}
                    variant="outline"
                    className="ml-2 bg-red-600 text-white hover:bg-red-700"
                  >
                    Logout
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    variant="default"
                    onClick={() => navigate("/login")}
                    className="bg-blue-700 text-white hover:bg-blue-800"
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
