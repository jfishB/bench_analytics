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
 * Styled to match the Godly-inspired dark design system (design-tokens.json).
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
        "Generate optimized lineups based on each batter's statistical profile.",
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
    <div className="space-y-16">
      {/* ---------- Hero Section ---------- */}
      <section className="relative overflow-hidden rounded-xl flex justify-center items-center min-h-[480px]">
        {/* Radial gradient background glow */}
        <div
          className="absolute inset-0 rounded-xl"
          style={{
            background:
              "radial-gradient(ellipse 80% 60% at 50% 50%, rgba(59,130,246,0.10) 0%, rgba(239,68,68,0.05) 60%, transparent 100%)",
            border: "1px solid rgba(255,255,255,0.06)",
          }}
        />
        <div className="relative text-center space-y-8 p-10 md:p-16 max-w-4xl">
          <h1 className="text-5xl md:text-7xl font-extrabold text-foreground tracking-tight">
            Your lineup.{" "}
            <span className="text-primary">Our analytics.</span>
            <br />
            <span className="text-accent">Their problem.</span>
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Stop guessing. Start winning. Our advanced analytics platform helps
            coaches optimize batting orders, analyze matchups, and make smarter
            decisions backed by data.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              size="lg"
              onClick={() => navigate("/lineup")}
              className="text-base px-8 py-6 bg-primary hover:bg-primary/90 text-white font-semibold shadow-glow-blue"
            >
              Start Optimizing
            </Button>

            <Button
              size="lg"
              onClick={() => navigate("/how-to-guide")}
              className="text-base px-8 py-6 font-semibold"
              style={{
                background: "rgba(255,255,255,0.05)",
                border: "1px solid rgba(255,255,255,0.12)",
                color: "var(--foreground)",
              }}
            >
              Learn How
            </Button>
          </div>
        </div>
      </section>

      {/* ---------- Features Section Header ---------- */}
      <div className="space-y-3 text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-foreground">
          Everything You Need to Win
        </h2>
        <p className="text-base text-muted-foreground">
          Comprehensive tools designed specifically for baseball coaches.
        </p>
      </div>

      {/* ---------- Features Grid ---------- */}
      <div className="grid md:grid-cols-2 gap-6 max-w-6xl mx-auto">
        {features.map((feature, index) => {
          const Icon = feature.icon;
          const isAccent = index % 2 === 1;
          return (
            <Card
              key={feature.title}
              style={
                isAccent
                  ? { boxShadow: "var(--shadow-glow-red)", borderColor: "rgba(239,68,68,0.18)" }
                  : {}
              }
            >
              <CardHeader>
                <div
                  className="w-12 h-12 rounded-md flex items-center justify-center mb-3"
                  style={{
                    background: isAccent
                      ? "rgba(239,68,68,0.12)"
                      : "rgba(59,130,246,0.12)",
                  }}
                >
                  <Icon
                    className="h-6 w-6"
                    style={{ color: isAccent ? "#ef4444" : "#3b82f6" }}
                  />
                </div>
                <CardTitle
                  style={{ color: isAccent ? "#ef4444" : "var(--foreground)" }}
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

      {/* ---------- Benefits Section ---------- */}
      <section
        className="rounded-xl p-10 max-w-6xl mx-auto"
        style={{
          background: "var(--surface)",
          border: "1px solid var(--border)",
        }}
      >
        <h2 className="text-3xl font-bold mb-10 text-center text-foreground">
          Key Benefits
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          {benefits.map((benefit) => {
            const Icon = benefit.icon;
            return (
              <div key={benefit.title} className="text-center space-y-4">
                <div
                  className="w-16 h-16 rounded-xl flex items-center justify-center mx-auto"
                  style={{ background: "rgba(59,130,246,0.12)" }}
                >
                  <Icon className="h-8 w-8 text-primary" />
                </div>
                <h3 className="font-semibold text-foreground">{benefit.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {benefit.description}
                </p>
              </div>
            );
          })}
        </div>
      </section>

      {/* ---------- CTA Section ---------- */}
      <section className="relative rounded-xl flex justify-center items-center min-h-[280px]">
        <div
          className="absolute inset-0 rounded-xl"
          style={{
            background:
              "radial-gradient(ellipse 80% 70% at 50% 50%, rgba(239,68,68,0.10) 0%, rgba(59,130,246,0.05) 60%, transparent 100%)",
            border: "1px solid rgba(255,255,255,0.06)",
          }}
        />
        <div className="relative text-center space-y-6 p-10 md:p-14 max-w-3xl">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground">
            Ready to Transform Your Team?
          </h2>
          <p className="text-lg text-muted-foreground">
            Start today and unlock tools that make every decision smarter,
            faster, and more confident.
          </p>
          <Button
            size="lg"
            onClick={() => navigate("/lineup")}
            className="text-base px-8 py-6 bg-accent hover:bg-accent/90 text-white font-semibold shadow-glow-red"
          >
            Start Building Lineups <MoveRight className="ml-2 h-5 w-5" />
          </Button>
        </div>
      </section>
    </div>
  );
};

export default Home;
