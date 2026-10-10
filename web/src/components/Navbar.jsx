import React, { useState } from 'react';
import { Hand, Github, Menu, X, Terminal } from 'lucide-react';

export default function Navbar({ repoUrl }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <nav className="navbar">
      <div className="container">
        <a href="#home" className="nav-brand">
          <div className="nav-logo-icon">
            <Hand size={20} />
          </div>
          <span className="nav-brand-text">
            Gesture<span className="gradient-text">Link</span>
          </span>
        </a>

        <ul className={`nav-links ${mobileOpen ? 'open' : ''}`}>
          <li><a href="#features" className="nav-link" onClick={() => setMobileOpen(false)}>Features</a></li>
          <li><a href="#gestures" className="nav-link" onClick={() => setMobileOpen(false)}>Gestures</a></li>
          <li><a href="#modes" className="nav-link" onClick={() => setMobileOpen(false)}>Modes</a></li>
          <li><a href="#simulator" className="nav-link" onClick={() => setMobileOpen(false)}>Simulator</a></li>
          <li><a href="#tech" className="nav-link" onClick={() => setMobileOpen(false)}>Tech Stack</a></li>
          <li><a href="#install" className="nav-link" onClick={() => setMobileOpen(false)}>Installation</a></li>
          <li>
            <a 
              href={repoUrl} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="btn btn-secondary"
              style={{ padding: '8px 16px', fontSize: '0.86rem' }}
            >
              <Github size={16} /> GitHub
            </a>
          </li>
        </ul>

        <button 
          className="mobile-menu-btn" 
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle navigation menu"
        >
          {mobileOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>
    </nav>
  );
}
