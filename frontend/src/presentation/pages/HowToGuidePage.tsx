import React from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../../ui/components/card";

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

      {/* Getting Started Section */}
      <section className="space-y-6">
        <h2 className="text-3xl text-primary">Getting Started</h2>

        {/* Step 1 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-900 text-white flex items-center justify-center font-bold">
                1
              </span>
              <span>Generate</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4">
              Let the algorithm create an optimized lineup.
            </p>
            <div className="space-y-2">
              <p className="font-semibold text-sm">Pro Tip:</p>
              <ul className="list-inside space-y-1 text-muted-foreground text-sm">
                <li>Update stats regularly for best results</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* Step 2 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-[var(--accent-red)] text-white flex items-center justify-center font-bold">
                2
              </span>
              <span>Review</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4">Review the recommendations and rationale.</p>
            <div className="space-y-2">
              <p className="font-semibold text-sm">Pro Tip:</p>
              <ul className="list-inside space-y-1 text-muted-foreground text-sm">
                <li>Adjust based on game importance</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
};

export default HowToGuide;
