import React from 'react';
import { 
  MousePointer, 
  ShieldCheck, 
  PenTool, 
  Tv, 
  Rocket, 
  Presentation, 
  Sliders, 
  Lock,
  Zap
} from 'lucide-react';

export default function Features() {
  const featureList = [
    {
      icon: <MousePointer size={24} style={{ color: '#00e5ff' }} />,
      bg: 'rgba(0, 229, 255, 0.1)',
      title: 'High-Precision Cursor Navigation',
      desc: 'Sub-millimeter tracking powered by adaptive Exponential Moving Average (EMA) smoothing and tremor deadzones for zero-jitter cursor control.'
    },
    {
      icon: <ShieldCheck size={24} style={{ color: '#10b981' }} />,
      bg: 'rgba(16, 185, 129, 0.1)',
      title: 'Multi-Frame Stability Engine',
      desc: '4-frame temporal validation, debounce cooldowns, and instant hardware fail-safe protection to eliminate accidental gestures and phantom clicks.'
    },
    {
      icon: <PenTool size={24} style={{ color: '#a855f7' }} />,
      bg: 'rgba(168, 85, 247, 0.1)',
      title: '3D Air Writing',
      desc: 'Draw vibrant, glowing color strokes in the air on live camera feed. Features multi-color cycle palette, gesture eraser, and instant high-res PNG export.'
    },
    {
      icon: <Tv size={24} style={{ color: '#38bdf8' }} />,
      bg: 'rgba(56, 189, 248, 0.1)',
      title: 'Virtual Digital Whiteboard',
      desc: 'A dedicated 1280x720 canvas designed for educators, presenters, and remote workers to sketch diagrams and erase mistakes in the air.'
    },
    {
      icon: <Rocket size={24} style={{ color: '#f59e0b' }} />,
      bg: 'rgba(245, 158, 11, 0.1)',
      title: 'Windows Application Launcher',
      desc: 'Gesture-driven circular quick menu to browse and safely launch Notepad, Calculator, File Explorer, Browsers, Paint, and custom executables.'
    },
    {
      icon: <Presentation size={24} style={{ color: '#ec4899' }} />,
      bg: 'rgba(236, 72, 153, 0.1)',
      title: 'Touchless Presentation Controller',
      desc: 'Deliver seamless slide decks in PowerPoint, Google Slides, or PDFs using directional hand gestures and horizontal swipe velocity detection.'
    },
    {
      icon: <Sliders size={24} style={{ color: '#6366f1' }} />,
      bg: 'rgba(99, 102, 241, 0.1)',
      title: 'Live Tuning & Persistence',
      desc: 'Real-time calibration for sensitivity sliders, pinch distance thresholds, and margin offsets saved automatically to local settings.json.'
    },
    {
      icon: <Lock size={24} style={{ color: '#00e5ff' }} />,
      bg: 'rgba(0, 229, 255, 0.1)',
      title: '100% Offline & Private',
      desc: 'Zero external API calls, zero telemetry, and zero accounts required. All computer vision models execute locally on your laptop CPU/GPU.'
    },
    {
      icon: <Zap size={24} style={{ color: '#f43f5e' }} />,
      bg: 'rgba(244, 63, 94, 0.1)',
      title: 'Emergency Stop Kill-Switch',
      desc: 'Press ESC at any millisecond to immediately disconnect automated mouse and keyboard controls for complete operator safety.'
    }
  ];

  return (
    <section id="features" className="section">
      <div className="container">
        <div className="section-header">
          <div className="section-tag">Key Capabilities</div>
          <h2 className="section-title">Engineered for Fluid, Reliable Touchless Control</h2>
          <p className="section-subtitle">
            GestureLink combines deep geometric hand analytics with robust system automation safeguards.
          </p>
        </div>

        <div className="grid-3">
          {featureList.map((item, index) => (
            <div key={index} className="glass-card feature-card">
              <div className="feature-icon-wrapper" style={{ background: item.bg }}>
                {item.icon}
              </div>
              <h3 className="feature-title">{item.title}</h3>
              <p className="feature-desc">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
