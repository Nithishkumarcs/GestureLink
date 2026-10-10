import React from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Features from './components/Features';
import Gestures from './components/Gestures';
import ModesShowcase from './components/ModesShowcase';
import InteractiveSimulator from './components/InteractiveSimulator';
import TechStack from './components/TechStack';
import Installation from './components/Installation';
import Footer from './components/Footer';

function App() {
  // Replace with your GitHub repository URL if customized
  const repoUrl = 'https://github.com/YOUR_GITHUB_USERNAME/GestureLink';

  return (
    <div className="app-root">
      <Navbar repoUrl={repoUrl} />
      <main>
        <Hero repoUrl={repoUrl} />
        <Features />
        <Gestures />
        <ModesShowcase />
        <InteractiveSimulator />
        <TechStack />
        <Installation repoUrl={repoUrl} />
      </main>
      <Footer repoUrl={repoUrl} />
    </div>
  );
}

export default App;
