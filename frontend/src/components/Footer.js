import React from "react";
import logo from "../assets/logo.png";
import { useNavigate } from "react-router-dom";

export function Footer() {
  const currentYear = new Date().getFullYear();
  const navigate = useNavigate();

  return (
    <footer className="bg-gray-50 border-t border-gray-200 mt-16">
      <div className="max-w-7xl mx-auto px-6 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10">
          {/* Logo + Description */}
          <div className="space-y-3">
            <img
              src={logo}
              alt="Bench Analytics"
              className="h-10 w-auto"
              onClick={() => navigate("/")}
            />
            <p className="text-sm text-gray-500 max-w-xs leading-relaxed">
              Advanced lineup optimization for baseball and softball coaches.
            </p>
          </div>

          {/* Product */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-3">
              Product
            </h4>
            <ul className="space-y-2 text-sm text-gray-500">
              <li
                className="hover:text-gray-700 cursor-pointer"
                onClick={() => navigate("/lineup")}
              >
                Lineup Optimizer
              </li>
              <li
                className="hover:text-gray-700 cursor-pointer"
                onClick={() => navigate("/lineup")}
              >
                Player Analytics
              </li>
              <li
                className="hover:text-gray-700 cursor-pointer"
                onClick={() => navigate("/lineup")}
              >
                Team Management
              </li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-3">
              Support
            </h4>
            <ul className="space-y-2 text-sm text-gray-500">
              <li className="hover:text-gray-700 cursor-pointer">
                How-to Guide
              </li>
              <li className="hover:text-gray-700 cursor-pointer">
                Documentation
              </li>
              <li className="hover:text-gray-700 cursor-pointer">
                Contact Support
              </li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-3">
              Company
            </h4>
            <ul className="space-y-2 text-sm text-gray-500">
              <li className="hover:text-gray-700 cursor-pointer">About Us</li>
              <li className="hover:text-gray-700 cursor-pointer">
                Privacy Policy
              </li>
              <li className="hover:text-gray-700 cursor-pointer">
                Terms of Service
              </li>
            </ul>
          </div>
        </div>

        {/* Divider + Copyright */}
        <div className="border-t border-gray-200 mt-10 pt-6 text-center text-sm text-gray-500">
          © {currentYear} Bench Analytics. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
