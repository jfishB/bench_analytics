import React from "react";
import AppRoutes from "./app/router/routes"; // TSX routes
import { Header } from "./ui/layout/Header";
import { Footer } from "./ui/layout/Footer";

const App: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-grow mt-24 px-4">
        <AppRoutes />
      </main>
      <Footer />
    </div>
  );
};

export default App;
