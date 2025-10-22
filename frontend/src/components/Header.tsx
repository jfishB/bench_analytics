import React from "react";
import logo from "../assets/logo.png";
import { Button } from "./ui/button";
import { useLocation, useNavigate } from "react-router-dom";

export function Header() {
  const location = useLocation();
  const navigate = useNavigate(); 
  
  const navItems = [
    { id: "home", label: "Home", path: "/" },
    { id: "optimizer", label: "Lineup Optimizer", path: "/lineup" },
    { id: "guide", label: "How-to Guide", path: "/guide" },
    { id: "about", label: "About Us", path: "/about" },
  ];

  const authItems = [
    { id: "login", label: "Login", path: "/login", variant: "outline" },
    { id: "register", label: "Register", path: "/register", variant: "default" },
  ];

  const activeSection = navItems.find(item => item.path === location.pathname)?.id;

  const activeAuth = authItems.find(item => item.path === location.pathname)?.id;

  return (
    <header className="border-b bg-card shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex h-20 items-center justify-between">
          <div className="flex items-center space-x-4">
            <img src={logo} alt="Bench Analytics" className="h-14 w-auto" />
            <h1 className="hidden sm:block text-xl text-primary font-semibold">
              Bench Analytics
            </h1>
          </div>
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => (
              <Button
                key={item.id}
                variant={activeSection === item.id ? "default" : "ghost"}
                onClick={() => {navigate(item.path);}}
                className="px-4"
              >
                {item.label}
              </Button>
            ))}

             {/* Divider */}
            <span className="text-muted-foreground mx-2 select-none text-lg">|</span>

            <div className="flex items-center space-x-2">
              {authItems.map((item) => (
                <Button
                  key={item.id}
                  variant={activeAuth === item.id ? "default" : "outline"}
                  onClick={() => navigate(item.path)}
                  className="ml-4 bg-blue-600 text-white hover:bg-blue-700"
                >
                  {item.label}
                </Button>
              ))}
            </div>

          </nav>

          {/* Mobile menu button
          <div className="md:hidden">
            <Button variant="ghost" size="sm">
              Menu
            </Button>
          </div>
          */}
        </div>  
        {/* Mobile navigation
        <div className="md:hidden pb-4">
          <div className="flex flex-wrap gap-2">
            {navItems.map((item) => (
              <Button
                key={item.id}
                variant={activeSection === item.id ? "default" : "ghost"}
                size="sm"
                onClick={() => setActiveSection(item.id)}
              >
                {item.label}
              </Button>
            ))}
          </div>
        </div>
        */}
      </div>
    </header>
  );
}
