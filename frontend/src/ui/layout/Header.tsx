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
    <header
      className="fixed top-0 left-0 right-0 z-50"
      style={{
        background: "var(--header-bg)",
        backdropFilter: "blur(12px)",
        WebkitBackdropFilter: "blur(12px)",
        borderBottom: "1px solid var(--border)",
      }}
    >
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
                className={
                  activeSection === item.id
                    ? "px-4 bg-primary text-white hover:bg-primary/90"
                    : "px-4 text-muted-foreground hover:text-foreground hover:bg-white/5"
                }
              >
                {item.label}
              </Button>
            ))}

            <span className="text-muted-foreground mx-2 select-none text-lg opacity-30">
              |
            </span>

            {/* --- Authentication Actions --- */}
            <div className="flex items-center space-x-3">
              {user ? (
                <>
                  <span className="text-sm text-muted-foreground">
                    Logged in as <strong className="text-foreground">{user}</strong>
                  </span>
                  <Button
                    onClick={logout}
                    variant="outline"
                    className="ml-2 border-accent/40 text-accent hover:bg-accent/10 hover:border-accent/60"
                  >
                    Logout
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    variant="ghost"
                    onClick={() => navigate("/login")}
                    className="text-muted-foreground hover:text-foreground hover:bg-white/5"
                  >
                    Login
                  </Button>
                  <Button
                    variant="default"
                    onClick={() => navigate("/register")}
                    className="bg-primary text-white hover:bg-primary/90 shadow-glow-blue"
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

