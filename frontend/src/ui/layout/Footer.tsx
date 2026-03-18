import React from "react";
import logo from "../assets/logo_transparent.png";
import { useNavigate } from "react-router-dom";

/**
 * Footer Component
 * Dark themed footer matching the Godly design system (slate-900 surface,
 * subtle white borders, muted text).
 */
export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear(); // Dynamic year for copyright
  const navigate = useNavigate(); // Used for client-side navigation

  return (
    <footer
      className="mt-16"
      style={{
        background: "var(--surface)",
        borderTop: "1px solid var(--border)",
      }}
    >
      <div className="max-w-7xl mx-auto px-6 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10">
          {/* --- Logo + Description --- */}
          <div className="space-y-3">
            <img
              src={logo}
              alt="Bench Analytics"
              className="h-10 w-auto cursor-pointer opacity-90 hover:opacity-100 transition-opacity"
              onClick={() => navigate("/")}
            />
            <p className="text-sm text-muted-foreground max-w-xs leading-relaxed">
              Advanced lineup optimization for baseball coaches.
            </p>
          </div>

          {/* --- Product Links --- */}
          <div>
            <h4 className="text-sm font-semibold text-foreground mb-3">
              Product
            </h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li
                className="hover:text-foreground cursor-pointer transition-colors"
                onClick={() => navigate("/lineup")}
              >
                Lineup Optimizer
              </li>
              <li
                className="hover:text-foreground cursor-pointer transition-colors"
                onClick={() => navigate("/lineup")}
              >
                Player Analytics
              </li>
              <li
                className="hover:text-foreground cursor-pointer transition-colors"
                onClick={() => navigate("/lineup")}
              >
                Team Management
              </li>
            </ul>
          </div>

          {/* --- Support Links --- */}
          <div>
            <h4 className="text-sm font-semibold text-foreground mb-3">
              Support
            </h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li
                className="hover:text-foreground cursor-pointer transition-colors"
                onClick={() => navigate("/how-to-guide")}
              >
                How-to Guide
              </li>
              <li
                className="hover:text-foreground cursor-pointer transition-colors"
                onClick={() => navigate("/how-to-guide")}
              >
                Documentation
              </li>
              <li
                className="hover:text-foreground cursor-pointer transition-colors"
                onClick={() => navigate("/how-to-guide")}
              >
                Contact Support
              </li>
            </ul>
          </div>

          {/* --- Company Links --- */}
          <div>
            <h4 className="text-sm font-semibold text-foreground mb-3">
              Company
            </h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li
                className="hover:text-foreground cursor-pointer transition-colors"
                onClick={() => navigate("/about")}
              >
                About Us
              </li>
              <li
                className="hover:text-foreground cursor-pointer transition-colors"
                onClick={() => navigate("/about")}
              >
                Privacy Policy
              </li>
              <li
                className="hover:text-foreground cursor-pointer transition-colors"
                onClick={() => navigate("/about")}
              >
                Terms of Service
              </li>
            </ul>
          </div>
        </div>

        {/* --- Divider + Copyright --- */}
        <div
          className="mt-10 pt-6 text-center text-sm text-muted-foreground"
          style={{ borderTop: "1px solid var(--border)" }}
        >
          © {currentYear} Bench Analytics. All rights reserved.
        </div>
      </div>
    </footer>
  );
};

