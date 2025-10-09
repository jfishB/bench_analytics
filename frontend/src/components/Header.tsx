import React from "react";

interface HeaderProps {
  activeSection: string;
  setActiveSection: (section: string) => void;
}

export function Header({ activeSection, setActiveSection }: HeaderProps) {
  const navItems = [
    { id: "home", label: "Home" },
    { id: "optimizer", label: "Lineup Optimizer" },
    { id: "guide", label: "How-to Guide" },
    { id: "about", label: "About Us" },
  ];

  return (
    <header style={{ borderBottom: '1px solid #ddd', padding: '1rem', backgroundColor: '#f8f9fa' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#333' }}>Bench Analytics</h1>
        </div>
        <nav style={{ display: 'flex', gap: '0.5rem' }}>
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveSection(item.id)}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: activeSection === item.id ? '#007bff' : 'transparent',
                color: activeSection === item.id ? 'white' : '#333',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: activeSection === item.id ? 'bold' : 'normal'
              }}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </div>

        {/* Mobile navigation */}
        <div className="md:hidden pb-4">
          <div className="flex flex-wrap gap-2">
            {navItems.map((item) => (
              <Button
                key={item.id}
                variant={activeSection === item.id ? "default" : "ghost"}
                size="sm"
                onClick={() => setActiveSection(item.id)}
              >
                {item.label}
              </Button>
            ))}
          </div>
        </div>
      </div>
    </header>
  );
}
