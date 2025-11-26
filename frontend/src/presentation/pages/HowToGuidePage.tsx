import React from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../../ui/components/card";

const ProTip: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <p className="text-sm">
    <span className="font-semibold">Pro Tip:</span>{" "}
    <span className="text-muted-foreground">{children}</span>
  </p>
);

/**
 * HowToGuide page component.
 * Provides a comprehensive guide on using the Lineup Optimizer,
 * including key metrics, best practices, and FAQs.
 */
const HowToGuide: React.FC = () => {
  return (
    <div className="px-4 md:px-12 lg:px-24 space-y-8">
      {/* Header Section */}
      <section className="text-center space-y-4">
        <h1 className="text-3xl mb-2 text-primary">
          How to Use the Lineup Optimizer
        </h1>
        <p className="text-muted-foreground">
          A step-by-step guide to creating optimal batting orders for your team.
        </p>
      </section>

      {/* Getting Started Section */}
      <section className="space-y-6">
        <h2 className="text-2xl text-primary">Getting Started</h2>

        {/* Step 1 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-900 text-white flex items-center justify-center font-bold">
                1
              </span>
              <span>Load Your Roster</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4">
              Open the Lineup Optimizer and input your full roster, including
              each player's current season statistics.
            </p>
            <ProTip>
              The more complete your data, the more precise the optimizer's
              recommendations will be. Include stats like batting averages,
              on-base percentage, and OPS when available.
            </ProTip>
          </CardContent>
        </Card>

        {/* Step 2 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-[var(--accent-red)] text-white flex items-center justify-center font-bold">
                2
              </span>
              <span>Generate a Lineup</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4">
              Navigate to the Generate Lineup tab and create a lineup based on
              your loaded roster.
            </p>
            <ProTip>
              Treat the lineup as guidance—you can manually adjust based on your
              strategy or player preferences.
            </ProTip>
          </CardContent>
        </Card>

        {/* Step 3 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-900 text-white flex items-center justify-center font-bold">
                3
              </span>
              <span>Review & Analyze</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4">
              Switch to the Analysis tab to review recommended lineups and the
              rationale behind each suggestion.
            </p>
            <ProTip>
              Consider other factors beyond the data—injuries, matchups, or
              player energy. The optimizer provides guidance, but ultimately
              coaches make the final decision.
            </ProTip>
          </CardContent>
        </Card>

        {/* Step 4 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-[var(--accent-red)] text-white flex items-center justify-center font-bold">
                4
              </span>
              <span>Maintain Accuracy</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4">
              Regularly update player stats to reflect their latest performance
              trends.
            </p>
            <ProTip>
              Small stat changes can significantly affect lineup
              recommendations, especially for tight matchups or critical games.
            </ProTip>
          </CardContent>
        </Card>
      </section>

      {/* Understanding Key Metrics Section */}
      <section className="space-y-4">
        <h2 className="text-2xl text-primary">Understanding Key Metrics</h2>

        <div className="grid md:grid-cols-2 gap-6">
          {/* wOBA Card */}
          <Card>
            <CardHeader className="pb-1">
              <CardTitle className="text-base font-semibold text-foreground">
                wOBA (Weighted On-Base Average)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-sm">
                Comprehensive metric that values each outcome appropriately.
              </p>
              <span className="inline-block bg-blue-100 text-blue-700 text-xs font-medium px-3 py-1 rounded-full">
                Above .320 is good, .380+ is excellent
              </span>
            </CardContent>
          </Card>

          {/* OBP Card */}
          <Card>
            <CardHeader className="pb-1">
              <CardTitle className="text-base font-semibold text-foreground">
                On-Base Percentage (OBP)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-sm">How often a player reaches base safely.</p>
              <span className="inline-block bg-blue-100 text-blue-700 text-xs font-medium px-3 py-1 rounded-full">
                Above .340 is good, .380+ is excellent
              </span>
            </CardContent>
          </Card>

          {/* ISO Card */}
          <Card>
            <CardHeader className="pb-1">
              <CardTitle className="text-base font-semibold text-foreground">
                ISO (Isolated Power)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-sm">
                Measures raw power by isolating extra-base hits (SLG minus AVG).
              </p>
              <span className="inline-block bg-blue-100 text-blue-700 text-xs font-medium px-3 py-1 rounded-full">
                Above .150 is good, .200+ is excellent
              </span>
            </CardContent>
          </Card>

          {/* K% Card */}
          <Card>
            <CardHeader className="pb-1">
              <CardTitle className="text-base font-semibold text-foreground">
                K% (Strikeout Rate)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-sm">
                Percentage of plate appearances ending in a strikeout (lower is
                better).
              </p>
              <span className="inline-block bg-blue-100 text-blue-700 text-xs font-medium px-3 py-1 rounded-full">
                Below 20% is good, under 15% is excellent
              </span>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Lineup Construction Best Practices */}
      <section className="space-y-4">
        <h2 className="text-2xl text-primary">
          Lineup Construction Best Practices
        </h2>

        <Card className="rounded-2xl">
          <CardContent className="px-6 py-5 space-y-6">
            {/* Card header text */}
            <div>
              <p className="text-base font-semibold text-foreground">
                Traditional Lineup Roles
              </p>
              <p className="text-base text-muted-foreground">
                Understanding where different player types typically bat
              </p>
            </div>

            {/* Roles grid */}
            <div className="grid md:grid-cols-3 gap-y-6 gap-x-10 text-base">
              {/* Leadoff */}
              <div className="space-y-1">
                <p className="font-semibold text-foreground">Leadoff (1st)</p>
                <p className="text-muted-foreground">
                  High OBP, good speed, sets the tone
                </p>
              </div>

              {/* Contact */}
              <div className="space-y-1">
                <p className="font-semibold text-foreground">Contact (2nd)</p>
                <p className="text-muted-foreground">
                  Good contact, can advance runners
                </p>
              </div>

              {/* Power */}
              <div className="space-y-1">
                <p className="font-semibold text-foreground">Power (3rd–5th)</p>
                <p className="text-muted-foreground">
                  Best hitters, drive in runs
                </p>
              </div>

              {/* Production */}
              <div className="space-y-1">
                <p className="font-semibold text-foreground">
                  Production (6th–7th)
                </p>
                <p className="text-muted-foreground">
                  Solid contributors, table setters
                </p>
              </div>

              {/* Defense First */}
              <div className="space-y-1">
                <p className="font-semibold text-foreground">
                  Defense First (8th–9th)
                </p>
                <p className="text-muted-foreground">
                  Weaker hitters, focus on defense
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Algorithm Explanation Section */}
      <section className="space-y-6">
        <h2 className="text-2xl text-primary">How the Algorithm Works</h2>

        <Card className="rounded-2xl">
          <CardContent className="px-6 py-5 space-y-6">
            {/* Card header text */}
            <div>
              <p className="text-base font-semibold text-foreground">
                Key Ideas
              </p>
              <p className="text-base text-muted-foreground">
                The principles the algorithm is based on
              </p>
            </div>

            {/* Ideas grid */}
            <div className="grid md:grid-cols-3 gap-y-6 gap-x-10 text-base">
              {/* Focus on Runs */}
              <div className="space-y-1">
                <p className="font-semibold text-foreground">Focus on Expected Runs</p>
                <p className="text-muted-foreground">
                  Runs and expected runs are at the core of Sabermetrics principles
                </p>
              </div>

              {/* Advanced Metrics */}
              <div className="space-y-1">
                <p className="font-semibold text-foreground">Advanced Metrics</p>
                <p className="text-muted-foreground">
                  Sabermetrics utilizes wide range of player statistics to evaluate batter contribution
                </p>
              </div>

              {/* BaseRuns */}
              <div className="space-y-1">
                <p className="font-semibold text-foreground">BaseRuns</p>
                <p className="text-muted-foreground">
                  A formula designed to estimate how many runs a team would be expected to score
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="rounded-2xl">
          <CardContent className="px-6 py-5 space-y-6">
            {/* Card header text */}
            <div>
              <p className="text-base font-semibold text-foreground">
                Algorithm Steps
              </p>
              <p className="text-base text-muted-foreground">
                Step by step breakdown of the lineup optimization process
              </p>
            </div>

            {/* Algorithm steps grid */}
            <div className="grid md:grid-cols-4 gap-y-6 gap-x-10 text-base">
              {/* Step 1 */}
              <div className="space-y-1">
                <CardTitle className="flex items-center gap-3">
                  <span className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-900 text-white flex items-center justify-center font-bold">
                    1
                  </span>
                  <span>Permute</span>
                </CardTitle>
                <p className="text-muted-foreground">
                  Take given 9 players and run 9 permutations of batting orders
                </p>
              </div>

              {/* Step 2 */}
              <div className="space-y-1">
                <CardTitle className="flex items-center gap-3">
                  <span className="flex-shrink-0 w-8 h-8 rounded-full bg-[var(--accent-red)] text-white flex items-center justify-center font-bold">
                    2
                  </span>
                  <span>Adjust</span>
                </CardTitle>
                <p className="text-muted-foreground">
                  For each lineup adjust player stats based on current position
                </p>
              </div>

              {/* Step 3 */}
              <div className="space-y-1">
                <CardTitle className="flex items-center gap-3">
                  <span className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-900 text-white flex items-center justify-center font-bold">
                    3
                  </span>
                  <span>Aggregate</span>
                </CardTitle>
                <p className="text-muted-foreground">
                  Use adjusted player stats and BaseRuns to estimate lineup score
                </p>
              </div>

              {/* Step 4 */}
              <div className="space-y-1">
                <CardTitle className="flex items-center gap-3">
                  <span className="flex-shrink-0 w-8 h-8 rounded-full bg-[var(--accent-red)] text-white flex items-center justify-center font-bold">
                    4
                  </span>
                  <span>Output</span>
                </CardTitle>
                <p className="text-muted-foreground">
                  Recommend lineup with highest expected runs based on data
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* FAQ Section */}
      <section className="space-y-4">
        <h2 className="text-2xl text-primary">Frequently Asked Questions</h2>

        <div className="space-y-3">
          {/* FAQ 1 */}
          <Card className="rounded-2xl">
            <CardContent className="px-6 py-4 space-y-1">
              <p className="text-sm md:text-base font-semibold text-foreground">
                How often should I update player statistics?
              </p>
              <p className="text-sm text-muted-foreground">
                Update stats at least weekly during the season, or after
                significant performance changes.
              </p>
            </CardContent>
          </Card>

          {/* FAQ 2 */}
          <Card className="rounded-2xl">
            <CardContent className="px-6 py-4 space-y-1">
              <p className="text-sm md:text-base font-semibold text-foreground">
                Should I always follow the generated lineup exactly?
              </p>
              <p className="text-sm text-muted-foreground">
                Use the generated lineup as a starting point. Consider factors
                like player confidence, recent streaks, and team chemistry that
                algorithms can&apos;t easily quantify.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  );
};

export default HowToGuide;
