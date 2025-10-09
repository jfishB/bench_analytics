import React from "react";
import logo from "../assets/logo.png";

interface HeaderProps {
  activeSection: string;
  setActiveSection: (section: string) => void;
}

export function Header({ activeSection, setActiveSection }: HeaderProps) {
  const navItems = [
    { id: "home", label: "Home" },
  ];

  return (
    <header style={{ 
      backgroundColor: '#f7fafc', 
      padding: '1.5rem 0',
      borderBottom: '1px solid #cbd5e0'
    }}>
      <div style={{ 
        maxWidth: '1000px', 
        margin: '0 auto', 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        padding: '0 2rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <img 
            src={logo} 
            alt="Bench Analytics" 
            style={{ height: '45px', width: 'auto' }}
          />
          <h1 style={{ 
            fontSize: '1.5rem', 
            fontWeight: '600', 
            color: '#1a202c',
            margin: 0
          }}>
            Bench Analytics
          </h1>
        </div>
      </div>
    </header>
  );
}
