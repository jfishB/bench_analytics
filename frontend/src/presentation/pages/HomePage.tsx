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
  Target,
  Zap,
  Award,
  Clock,
  Repeat,
  SquarePen,
  MoveRight,
} from "lucide-react";

/**
 * Represents a displayable item (feature or benefit) on the home page.
 */
interface DisplayItem {
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
  const features: DisplayItem[] = [
    {
      title: "Smart Lineup Generation",
      description:
        "A powerful algorithm that analyzes player stats to generate optimal batting orders in seconds.",
      icon: Zap,
    },
    {
      title: "Player Performance Tracking",
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
        "Update player statistics to have the algorithm generate lineups based on the latest performance data",
      icon: SquarePen,
    },
  ];

  // List of benefits coaches gain from using the platform
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
  ];

  return (
    <div className="space-y-12">
      {/* ---------- Hero Section ---------- */}
      {/* Introduces the platform and main call-to-action buttons */}
      <section className="relative overflow-hidden rounded-lg flex justify-center items-center min-h-[400px]">
        <div className="absolute left-1/2 -translate-x-1/2 top-1/2 -translate-y-1/2 w-[calc(100%-1rem)] max-w-6xl h-[400px] bg-gradient-to-r from-blue-900/10 to-red-600/10 rounded-2xl" />
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
              key={feature.title}
              className={index % 2 === 1 ? "border-[var(--accent-red)]/20" : ""}
            >
              <CardHeader>
                <div
                  className={`w-12 h-12 rounded-lg flex items-center justify-center mb-3 ${
                    index % 2 === 1 ? "bg-red-600/10" : "bg-blue-900/10"
                  }`}
                >
                  <Icon
                    className={`h-6 w-6 ${
                      index % 2 === 1 ? "text-red-600" : "text-blue-900"
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

      {/* ---------- Benefits Grid ---------- */}
      {/* Displays our benefits in block */}

      <section className="bg-gray-100/50 rounded-lg p-8 max-w-6xl mx-auto">
        <h2 className="text-3xl mb-8 text-center text-primary">Key Benefits</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {benefits.map((benefit, index) => {
            const Icon = benefit.icon;
            return (
              <div key={benefit.title} className="text-center space-y-3">
                <div className="w-16 h-16 rounded-full bg-blue-900/10 flex items-center justify-center mx-auto">
                  <Icon className="h-8 w-8 text-blue-900" />
                </div>
                <h3 className="font-medium">{benefit.title}</h3>
                <p className="text-sm text-muted-foreground">
                  {benefit.description}
                </p>
              </div>
            );
          })}
        </div>
      </section>

      {/* ---------- CTA Section ---------- */}
      {/* Final call-to-action to encourage signup */}
      <section className="relative rounded-2xl flex justify-center items-center min-h-[250px]">
        <div className="absolute left-1/2 -translate-x-1/2 top-1/2 -translate-y-1/2 w-[calc(100%-1rem)] max-w-6xl h-[250px] bg-gradient-to-r from-blue-900/10 to-red-600/10 rounded-2xl" />
        <div className="relative text-center space-y-6 p-8 md:p-12 max-w-4xl">
          <h2 className="text-2xl md:text-4xl text-primary">
            Ready to Transform Your Team?
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground">
            Start today and unlock tools that make every decision smarter,
            faster, and more confident.
          </p>
          <Button
            size="lg"
            onClick={() => navigate("/lineup")}
            className="text-lg px-8 py-6 bg-red-600 hover:bg-red-700"
          >
            Start Building Lineups <MoveRight className="ml-2 h-5 w-5" />
          </Button>
        </div>
      </section>
    </div>
  );
};

export default Home;
