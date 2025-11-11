import React from "react";
import AppRoutes from "./app/router/routes"; // TSX routes
import { Header } from "./ui/layout/Header";
import { Footer } from "./ui/layout/Footer";

/**
 * App (Root Component)
 *
 * - Wraps the entire application
 * - Provides consistent layout with Header and Footer
 * - Renders the routed pages inside the main content area
 */
const App: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Global header */}
      <Header />

      {/* Main content area where routes are rendered */}
      <main className="flex-grow mt-24 px-4">
        <AppRoutes />
      </main>

      {/* Global footer */}
      <Footer />
    </div>
  );
};

export default App;
