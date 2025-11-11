import React from "react";
import ReactDOM from "react-dom/client";
import "./ui/theme/index.css"; // global styles
import App from "./App";
import { BrowserRouter } from "react-router-dom";

/**
 * Entry point for the React application
 * - Mounts the root component to the DOM
 * - Wraps App in BrowserRouter for client-side routing
 * - Wraps App in StrictMode for highlighting potential issues
 */
const rootElement = document.getElementById("root");
if (!rootElement) throw new Error("Root element not found"); // fail early if root container is missing

const root = ReactDOM.createRoot(rootElement as HTMLElement);

root.render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
