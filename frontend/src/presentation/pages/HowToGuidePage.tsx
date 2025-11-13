import React from "react";

const HowToGuide: React.FC = () => {
  return (
    <div className="space-y-12 max-w-6xl mx-auto">
      {/* Header Section */}
      <section className="text-center space-y-4">
        <h1 className="text-3xl mb-2 text-primary">
          How to Use the Lineup Optimizer
        </h1>
        <p className="text-muted-foreground">
          A step-by-step guide to creating optimal batting orders for your team
        </p>
      </section>
    </div>
  );
};

export default HowToGuide;
