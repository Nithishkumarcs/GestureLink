import React from 'react';
import { Github, Play, ShieldAlert, Cpu, Terminal, Sparkles, Layers } from 'lucide-react';

export default function Hero({ repoUrl }) {
  return (
    <section id="home" className="hero">
      <div className="container">
        <div className="hero-content">
          <div className="hero-badge">
            <span className="hero-badge-dot"></span>
            Vision-Based Touchless Laptop Control
          </div>

          <h1 className="hero-title">
            Transform Your Webcam Into A <br />
            <span className="gradient-text">Spatial Touchless Interface</span>
          </h1>

          <p className="hero-desc">
            GestureLink is an advanced, offline Python computer vision desktop system that enables 
            sub-millimeter mouse control, 3D air writing, virtual whiteboarding, and slide control—using 
            only your standard laptop webcam and real-time hand tracking.
          </p>

          <div className="hero-cta">
            <a href="#install" className="btn btn-primary">
              <Terminal size={18} /> Get Started & Run Locally
            </a>
            <a href={repoUrl} target="_blank" rel="noopener noreferrer" className="btn btn-secondary">
              <Github size={18} /> Star on GitHub
            </a>
          </div>

          {/* Transparent Accuracy Banner */}
          <div className="disclaimer-banner">
            <ShieldAlert size={22} style={{ color: '#38bdf8', flexShrink: 0 }} />
            <div>
              <strong>Architecture Note:</strong> GestureLink operates as a high-performance local Python 
              desktop application for privacy and security. This web frontend is an interactive showcase, documentation portal, 
              and gesture simulator—it runs locally on your machine when executed via Python.
            </div>
          </div>

          {/* HUD Window Mockup Preview */}
          <div className="hero-mockup-frame">
            <div className="mockup-inner">
              <div className="mockup-topbar">
                <div className="window-dots">
                  <div className="dot dot-red"></div>
                  <div className="dot dot-yellow"></div>
                  <div className="dot dot-green"></div>
                </div>
                <div className="mockup-badge">
                  GESTURELINK DESKTOP HUD &bull; 640x480 @ 30 FPS
                </div>
                <div style={{ color: '#10b981', fontSize: '0.75rem', fontFamily: 'var(--font-mono)' }}>
                  ● SYSTEM READY
                </div>
              </div>

              <div className="mockup-display">
                {/* Left Mini Sidebar */}
                <div style={{ padding: '20px', borderRight: '1px solid rgba(255,255,255,0.06)', textAlign: 'left', background: '#0a0e1a' }}>
                  <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 700, marginBottom: '14px' }}>CONTROL MODES</div>
                  <div style={{ background: '#1e293b', color: '#38bdf8', padding: '8px 12px', borderRadius: '8px', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>
                    🖱️ Mouse Control
                  </div>
                  <div style={{ color: '#94a3b8', padding: '8px 12px', fontSize: '0.85rem' }}>✍️ Air Writing</div>
                  <div style={{ color: '#94a3b8', padding: '8px 12px', fontSize: '0.85rem' }}>📋 Whiteboard</div>
                  <div style={{ color: '#94a3b8', padding: '8px 12px', fontSize: '0.85rem' }}>🚀 App Launcher</div>
                  <div style={{ color: '#94a3b8', padding: '8px 12px', fontSize: '0.85rem' }}>📊 Presentation</div>
                </div>

                {/* Center Video Area Mockup */}
                <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#05070d', overflow: 'hidden' }}>
                  <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(rgba(56, 189, 248, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(56, 189, 248, 0.05) 1px, transparent 1px)', backgroundSize: '30px 30px' }}></div>
                  
                  {/* Interaction Boundary Box */}
                  <div style={{ width: '70%', height: '70%', border: '1px dashed #00e5ff', borderRadius: '12px', position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 25px rgba(0, 229, 255, 0.1)' }}>
                    <div style={{ position: 'absolute', top: '8px', left: '12px', color: '#00e5ff', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>
                      INTERACTION ZONE (EMA 0.60)
                    </div>
                    {/* Simulated Hand Landmark Node */}
                    <div style={{ width: '14px', height: '14px', borderRadius: '50%', background: '#00e5ff', boxShadow: '0 0 16px #00e5ff', position: 'absolute', top: '35%', left: '48%' }}>
                      <div style={{ position: 'absolute', top: '-24px', left: '16px', background: '#0f172a', border: '1px solid #00e5ff', color: '#00e5ff', fontSize: '0.7rem', padding: '2px 6px', borderRadius: '4px', whiteSpace: 'nowrap', fontFamily: 'var(--font-mono)' }}>
                        INDEX_TIP (x:0.48, y:0.35)
                      </div>
                    </div>
                    <div style={{ color: '#64748b', fontSize: '0.85rem' }}>Camera Stream Active</div>
                  </div>
                </div>

                {/* Right Telemetry Column */}
                <div style={{ padding: '20px', borderLeft: '1px solid rgba(255,255,255,0.06)', textAlign: 'left', background: '#0a0e1a' }}>
                  <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 700, marginBottom: '8px' }}>DETECTED GESTURE</div>
                  <div style={{ background: '#131b2e', padding: '12px', borderRadius: '10px', textAlign: 'center', marginBottom: '16px' }}>
                    <div style={{ fontSize: '1.8rem', marginBottom: '4px' }}>☝️</div>
                    <div style={{ color: '#38bdf8', fontWeight: 700, fontSize: '0.95rem' }}>INDEX FINGER</div>
                    <div style={{ fontSize: '0.75rem', color: '#10b981' }}>Cursor Navigation Active</div>
                  </div>

                  <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 700, marginBottom: '6px' }}>CONFIDENCE & STABILITY</div>
                  <div style={{ height: '6px', width: '100%', background: '#1e293b', borderRadius: '3px', overflow: 'hidden', marginBottom: '14px' }}>
                    <div style={{ width: '92%', height: '100%', background: '#00e5ff' }}></div>
                  </div>

                  <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 700, marginBottom: '4px' }}>SAFETY ENGINE</div>
                  <div style={{ fontSize: '0.8rem', color: '#10b981', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    ● FailSafe Enabled (ESC)
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
