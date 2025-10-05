export default function App() {
  return <div>Hello, World!</div>;

  /*const [activeSection, setActiveSection] = useState('home');

  const renderContent = () => {
    switch (activeSection){
      case 'home':
        return <Home setActiveSection={setActiveSection}/>;
      case 'optimizer':
        return <LineupOptimizer />
      case 'guide':
        return <HowToGuide />
      case 'about':
        return <About />
      default:
        return <Home setActiveSection={setActiveSection}/>; 
    }
  }
  */
}