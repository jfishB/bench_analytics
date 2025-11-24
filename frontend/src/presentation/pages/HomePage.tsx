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
import {
  BarChart3,
  Lightbulb,
  Target,
  Zap,
  Award,
  Clock,
  Repeat,
  SquarePen,
  MoveRight,
} from "lucide-react";

/**
 * Represents a key product feature displayed on the home page.
 */
interface Feature {
  title: string;
  description: string;
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
        "Data-powered algorithms analyze player stats to suggest optimal batting orders",
    },
    {
      title: "Player Analytics",
      description:
        "Preview hits, OBP, plate appearances, and more for every player on your roster.",
      icon: BarChart3,
    },
    {
      title: "Matchup Analysis",
      description:
        "Generate optimized lineups based on each batter’s statistical profile.",
      icon: Target,
    },
    {
      title: "Quick Adjustments",
      description:
        "Update player statistics to have the algorithm lineups based on the latest performance data",
      icon: SquarePen,
    },
  ];

  const benefits: DisplayItem[] = [
    {
      icon: Award,
      title: "Win More Games",
      description: "Data-driven decisions lead to better outcomes.",
    },
    {
      icon: Clock,
      title: "Save Time",
      description: "Generate lineups in seconds, not hours.",
    },
    {
      icon: Repeat,
      title: "Reliable, Repeatable Process",
      description:
        "Eliminate guesswork with a consistent system for lineup creation.",
    },
    {
      icon: Lightbulb,
      title: "Easy to understand",
      description: "Designed to be intuitive and simple for coaches to use.",
    },
  ];

  return (
    <div className="space-y-12">
      {/* ---------- Hero Section ---------- */}
      {/* Introduces the platform and main call-to-action buttons */}
      <section className="text-center py-12">
        <div className="max-w-3xl mx-auto space-y-6">
          <h1 className="text-4xl md:text-6xl text-primary">
            Your lineup. Our analytics.
            <br />
            <span className="text-red-600">Their problem.</span>
          </h1>
          <p className="text-xl text-muted-foreground">
            Advanced analytics and data-powered insights to help coaches build
            winning lineups based on player performance, matchups, and game
            situations.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" onClick={() => navigate("/lineup")}>
              Start Optimizing
            </Button>

            <Button
              size="lg"
              onClick={() => navigate("/how-to-guide")}
              style={{
                border: "1px solid rgba(0, 0, 0, 0.2)",
                color: "rgba(0,0,0,0.7)",
                padding: "0 2rem",
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
      <section className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
        {features.map((feature, index) => (
          <Card
            key={index}
            className={index % 2 === 1 ? "border-[var(--accent-red)]/20" : ""}
          >
            <CardHeader>
              <CardTitle
                className={
                  index % 2 === 1 ? "text-[var(--accent-red)]" : "text-primary"
                }
              >
                {feature.title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-base">
                {feature.description}
              </CardDescription>
            </CardContent>
          </Card>
        ))}
      </section>
    </div>
  );
};

export default Home;
