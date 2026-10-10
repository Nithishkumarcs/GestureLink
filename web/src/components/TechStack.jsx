import React from 'react';
import { Cpu, Eye, Hand, Layers, Monitor, Terminal } from 'lucide-react';

export default function TechStack() {
  const stack = [
    {
      name: 'Python 3.11',
      role: 'Core Runtime & Lifecycle',
      desc: 'Powers concurrent threading, state management, and operating system controller integration.',
      icon: '🐍'
    },
    {
      name: 'OpenCV 4.8+',
      role: 'Computer Vision & Camera Engine',
      desc: 'Handles high-speed frame capture, mirroring, HUD rendering, and sensor auto-exposure.',
      icon: '📷'
    },
    {
      name: 'Google MediaPipe',
      role: '21-Point 3D Hand Tracking',
      desc: 'Executes lightweight TFLite inference to track fingertip joints with sub-millimeter spatial accuracy.',
      icon: '🖐️'
    },
    {
      name: 'PyAutoGUI',
      role: 'OS Automation Controller',
      desc: 'Executes programmatic mouse cursor movements, clicks, double clicks, scrolls, and shortcuts.',
      icon: '🖱️'
    },
    {
      name: 'Tkinter & PIL',
      role: 'Desktop Dashboard GUI',
      desc: 'Renders the dark cyber control center, telemetry progress bars, and high-performance video canvas.',
      icon: '🖥️'
    },
    {
      name: 'React 18 & Vite',
      role: 'Web Companion & Documentation',
      desc: 'Ultra-fast, responsive web portal providing interactive gesture simulations and setup guides.',
      icon: '⚡'
    }
  ];

  return (
    <section id="tech" className="section">
      <div className="container">
        <div className="section-header">
          <div className="section-tag">Architecture & Tools</div>
          <h2 className="section-title">Built On Modern Vision & Python Technologies</h2>
          <p className="section-subtitle">
            Engineered with zero heavy external cloud dependencies—fast, private, and fully offline.
          </p>
        </div>

        <div className="tech-grid">
          {stack.map((item, i) => (
            <div key={i} className="tech-card">
              <div style={{ fontSize: '2.4rem', marginBottom: '10px' }}>{item.icon}</div>
              <h3 className="tech-badge-title">{item.name}</h3>
              <div className="tech-role">{item.role}</div>
              <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '10px', lineHeight: 1.5 }}>
                {item.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
