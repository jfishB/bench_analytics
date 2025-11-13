import React from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../../ui/components/card";

/**
 * Type definition for each team member displayed on the About page.
 */
interface TeamMember {
  name: string;
  background: string;
}

/**
 * About page component for Bench Analytics.
 * Displays the mission statement, team members, and contact information.
 */
export const About: React.FC = () => {
  // List of team members and their backgrounds
  const teamMembers: TeamMember[] = [
    {
      name: "Jeevesh Balendra",
      background:
        "Computer Science Specialist passionate about problem-solving and innovation.",
    },
    {
      name: "Lea Palme",
      background:
        "Computer Science Specialist and Cognitive Science major exploring Cyber security and sustainable technology.",
    },
    {
      name: "Ilya Kononov",
      background: "Computer Science and Mathematics major interested in cloud development and optimization",
    },
    {
      name: "Luke Pan",
      background:
        "Computer Science Specialist with an interest in full-stack development.",
    },
    {
      name: "Rashu Sharda",
      background:
        "Computer Science Specialist with a Math minor, passionate about software development.",
    },
  ];

  return (
    <div className="px-4 md:px-12 lg:px-24 space-y-8">
      {/* ---------- Page Header ---------- */}
      <div className="text-center">
        <h1 className="text-3xl mb-2 text-primary">About Bench Analytics</h1>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          We're passionate about helping coaches make data-driven decisions that
          lead to more wins on the field.
        </p>
      </div>

      {/* ---------- Mission Statement ---------- */}
      <section className="text-center py-8">
        <div className="max-w-3xl mx-auto space-y-6">
          <h2 className="text-2xl text-primary">Our Mission</h2>
          <p className="text-lg text-muted-foreground">
            To democratize advanced baseball analytics and give every coach,
            regardless of budget or technical expertise, access to the same
            data-driven insights used by professional teams.
          </p>
        </div>
      </section>

      {/* ---------- Team Section ---------- */}
      <section className="space-y-6">
        <h2 className="text-2xl text-primary">Meet Our Team</h2>
        <div className="grid md:grid-cols-2 gap-6">
          {teamMembers.map((member, index) => (
            <Card key={index}>
              <CardHeader>
                <div className="flex items-center space-x-3">
                  {/* Circle with member initials */}
                  <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center text-primary-foreground">
                    {member.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")}
                  </div>
                  {/* Member name */}
                  <div>
                    <CardTitle className="text-lg">{member.name}</CardTitle>
                  </div>
                </div>
              </CardHeader>
              {/* Member background / short bio */}
              <CardContent>
                <p className="text-sm">{member.background}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* ---------- Contact Section ---------- */}
      <section className="space-y-6">
        <h2 className="text-2xl text-primary">Get in Touch</h2>
        {/* Contact card with support and partnership info */}
        <Card>
          <CardContent className="pt-6">
            <div className="grid md:grid-cols-2 gap-6">
              {/* Support Contact */}
              <div>
                <h4 className="font-medium mb-2">Support</h4>
                <p className="text-sm text-muted-foreground mb-2">
                  Need help or have questions? Our team is here to support you.
                </p>
                <p className="text-sm">support@benchanalytics.com</p>
              </div>
              {/* Partnerships Contact */}
              <div>
                <h4 className="font-medium mb-2">Partnerships</h4>
                <p className="text-sm text-muted-foreground mb-2">
                  Interested in partnering with us or bulk licensing?
                </p>
                <p className="text-sm">partnerships@benchanalytics.com</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
};

export default About;
