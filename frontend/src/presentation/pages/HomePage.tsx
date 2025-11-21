import React from "react";
import { Button } from "../../ui/components/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "../../ui/components/card";
import { useNavigate } from "react-router-dom";
import { BarChart3, TrendingUp, Target, Zap } from "lucide-react";

/**
 * Represents a key product feature displayed on the home page.
 */
interface Feature {
  title: string;
  description: string;
  icon: React.ComponentType<any>;
}

/**
 * Home page component — introduces Bench Analytics and highlights
 * its main features to encourage user engagement.
 */
const Home: React.FC = () => {
  const navigate = useNavigate();

  // List of major platform features shown on the home screen
  const features: Feature[] = [
    {
      title: "Smart Lineup Generation",
      description:
        "A powerful algorithm that analyzes player stats to generate optimal batting orders in seconds.",
      icon: Zap,
    },
    {
      title: "Player Performance Tracking",
      description:
        "Track hits, OBP, plate appearances, and more for every player on your roster.",
      icon: BarChart3,
    },
    {
      title: "Matchup Analysis",
      description:
        "Optimize lineups based on opposing pitcher handedness, historical matchup data, and platoon advantages.",
      icon: Target,
    },
    {
      title: "Real-time Adjustments",
      description:
        "Make in-game lineup changes and substitutions based on live game situations and player performance.",
      icon: TrendingUp,
    },
  ];

  return (
    <div className="space-y-12">
      {/* ---------- Hero Section ---------- */}
      {/* Introduces the platform and main call-to-action buttons */}
      <section className="relative overflow-hidden rounded-lg flex justify-center items-center min-h-[400px]">
        <div className="absolute left-1/2 -translate-x-1/2 top-1/2 -translate-y-1/2 w-[calc(100%-2rem)] max-w-6xl h-[400px] bg-gradient-to-r from-blue-900/10 to-red-600/10 rounded-2xl" />
        <div className="relative text-center space-y-6 p-8 md:p-12 max-w-4xl">
          <h1 className="text-4xl md:text-6xl text-primary">
            Your lineup. Our analytics.
            <br />
            <span className="text-red-600">Their problem.</span>
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground">
            Stop guessing. Start winning. Our advanced analytics platform helps
            coaches optimize batting orders, analyze matchups, and make smarter
            decisions backed by data.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              size="lg"
              onClick={() => navigate("/lineup")}
              className="text-lg px-8 py-6"
            >
              Start Optimizing
            </Button>

            <Button
              size="lg"
              onClick={() => navigate("/how-to-guide")}
              className="text-lg px-8 py-6"
              style={{
                border: "1px solid rgba(0, 0, 0, 0.2)",
                color: "rgba(0,0,0,0.7)",
                backgroundColor: "transparent",
              }}
            >
              Learn How
            </Button>
          </div>
        </div>
      </section>

      {/* ---------- Features Grid ---------- */}
      {/* Displays key platform features in a responsive grid of cards */}
      <div className="space-y-2">
        <h2 className="text-xl md:text-3xl text-primary text-center">
          Everything You Need to Win
        </h2>
        <h3 className="text-base text-center text-muted-foreground">
          Comprehensive tools designed specifically for baseball coaches.
        </h3>
      </div>
      <div className="grid md:grid-cols-2 gap-6 max-w-6xl mx-auto">
        {features.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <Card
              key={index}
              className={index % 2 === 1 ? "border-[var(--accent-red)]/20" : ""}
            >
              <CardHeader>
                <div
                  className={`w-12 h-12 rounded-lg flex items-center justify-center mb-3 ${
                    index % 2 === 1
                      ? "bg-[var(--accent-red)]/10"
                      : "bg-primary/10"
                  }`}
                >
                  <Icon
                    className={`h-6 w-6 ${
                      index % 2 === 1
                        ? "text-[var(--accent-red)]"
                        : "text-primary"
                    }`}
                  />
                </div>
                <CardTitle
                  className={
                    index % 2 === 1
                      ? "text-[var(--accent-red)]"
                      : "text-primary"
                  }
                >
                  {feature.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>{feature.description}</CardDescription>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

export default Home;
