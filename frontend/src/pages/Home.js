import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";


export default function Home({ setActiveSection }) {
  const features = [
    {
      title: "Smart Lineup Generation",
      description: "Data-powered algorithms analyze player stats to suggest optimal batting orders"
    },
    {
      title: "Player Analytics",
      description: "Comprehensive player performance tracking and statistical analysis"
    }
  ]

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center py-12">
        <div className="max-w-3xl mx-auto space-y-6">
          <h1 className="text-4xl md:text-6xl text-primary">
            Optimize Your Baseball Lineups
          </h1>
          <p className="text-xl text-muted-foreground">
            Advanced analytics and data-powered insights to help coaches build winning lineups 
            based on player performance, matchups, and game situations.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              size="lg" 
              onClick={() => setActiveSection('optimizer')}
              className="px-8 bg-[var(--accent-red)] text-[var(--accent-red-foreground)] hover:bg-[var(--accent-red)]/90"
            >
              Start Optimizing
            </Button>
            <Button 
              variant="outline" 
              size="lg"
              onClick={() => setActiveSection('guide')}
              className="px-8"
            >
              Learn How
            </Button>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
        {features.map((feature, index) => (
          <Card key={index} className={index % 2 === 1 ? "border-[var(--accent-red)]/20" : ""}>
            <CardHeader>
              <CardTitle className={index % 2 === 1 ? "text-[var(--accent-red)]" : "text-primary"}>
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
  )
}
