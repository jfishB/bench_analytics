import React, { useState } from "react";
import { Header } from './components/Header';



export default function App() {
  const [activeSection, setActiveSection] = useState('home');

  /*const renderContent = () => {
    switch (activeSection){
      case 'home':
        return <Home setActiveSection={setActiveSection}/>;
      case 'optimizer':
        return <LineupOptimizer />;
      case 'guide':
        return <HowToGuide />;
      case 'about':
        return <About />;
      default:
        return <Home setActiveSection={setActiveSection}/>; 
    }
  }*/

  return (
    <div>
      <Header activeSection={activeSection} setActiveSection={setActiveSection}/>
    </div>
  );
}