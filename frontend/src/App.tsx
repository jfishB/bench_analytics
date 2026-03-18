import React from "react";
import AppRoutes from "./app/router/routes"; // TSX routes
import { Header } from "./ui/layout/Header";
import { Footer } from "./ui/layout/Footer";
import { AuthProvider } from "./services/AuthContext";

/**
 * App (Root Component)
 *
 * - Wraps the entire application
 * - Provides consistent layout with Header and Footer
 * - Applies the Godly-inspired dark theme (slate-950 background, design-tokens.json)
 * - Renders the routed pages inside the main content area
 */
const App: React.FC = () => {
  return (
    <AuthProvider>
      {/* dark class activates the slate-950/900 dark design system */}
      <div className="dark min-h-screen flex flex-col bg-background text-foreground">
        {/* Global header */}
        <Header />

        {/* Main content area where routes are rendered */}
        <main className="flex-grow mt-24 px-4">
          <AppRoutes />
        </main>

        {/* Global footer */}
        <Footer />
      </div>
    </AuthProvider>
  );
};

export default App;

