import React, { useState } from "react";
import { Header } from "./components/Header2";
import { Home } from "./components/Home";

function App() {
  const [activeSection, setActiveSection] = useState("home");

  const renderContent = () => {
    switch (activeSection){
      case 'home':
        return <Home setActiveSection={setActiveSection}/>;
      default:
        return <Home setActiveSection={setActiveSection}/>; 
    }
  }

  return (
    <div>
      <Header
        activeSection={activeSection}
        setActiveSection={setActiveSection}
      />
      {renderContent()}
    </div>
  );
}

export default App;
