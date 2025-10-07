import React from "react";
import logo from "../assets/logo.png";
import { Button } from "./ui/button";

interface HeaderProps {
  activeSection: string;
  setActiveSection: (section: string) => void;
}

export function Header({ activeSection, setActiveSection }: HeaderProps) {
  const navItems = [
    { id: "home", label: "Home" },
    { id: "optimizer", label: "Lineup Optimizer" },
    { id: "guide", label: "How-to Guide" },
    { id: "about", label: "About Us" },
  ];

  return (
    <header className="border-b bg-card shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex h-18 items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <img src={logo} alt="Bench Analytics" className="h-14 w-auto" />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-xl text-primary">Bench Analytics</h1>
            </div>
          </div>
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => (
              <Button
                key={item.id}
                variant={activeSection === item.id ? "default" : "ghost"}
                onClick={() => setActiveSection(item.id)}
                className="px-4"
              >
                {item.label}
              </Button>
            ))}
          </nav>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <Button variant="ghost" size="sm">
              Menu
            </Button>
          </div>
        </div>

        {/* Mobile navigation */}
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
      </div>
    </header>
  );
}
