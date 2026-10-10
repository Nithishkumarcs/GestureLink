import React from 'react';
import { Hand, Github, Shield, Heart } from 'lucide-react';

export default function Footer({ repoUrl }) {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-brand">
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
              <div className="nav-logo-icon" style={{ width: '30px', height: '30px' }}>
                <Hand size={16} />
              </div>
              <span style={{ fontSize: '1.2rem', fontWeight: 800 }}>
                Gesture<span className="gradient-text">Link</span>
              </span>
            </div>
            <p style={{ color: '#94a3b8', fontSize: '0.88rem', lineHeight: 1.6 }}>
              Vision-Based Touchless Laptop Control System. Open-source, private, and 100% offline computer vision software.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '32px', flexWrap: 'wrap' }}>
            <div>
              <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#38bdf8', textTransform: 'uppercase', marginBottom: '12px' }}>
                Project Links
              </div>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.88rem' }}>
                <li><a href={repoUrl} target="_blank" rel="noopener noreferrer" style={{ color: '#94a3b8', textDecoration: 'none' }}>GitHub Repository</a></li>
                <li><a href="#gestures" style={{ color: '#94a3b8', textDecoration: 'none' }}>Gesture Guide</a></li>
                <li><a href="#modes" style={{ color: '#94a3b8', textDecoration: 'none' }}>Control Modes</a></li>
                <li><a href="#install" style={{ color: '#94a3b8', textDecoration: 'none' }}>Setup Guide</a></li>
              </ul>
            </div>

            <div>
              <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#38bdf8', textTransform: 'uppercase', marginBottom: '12px' }}>
                Trust & Security
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.85rem', color: '#94a3b8' }}>
                <span>🔒 100% Offline Processing</span>
                <span>🛡️ PyAutoGUI Fail-Safe</span>
                <span>📄 MIT Licensed</span>
              </div>
            </div>
          </div>
        </div>

        <div className="footer-copy">
          &copy; {new Date().getFullYear()} GestureLink &bull; Built with MediaPipe, OpenCV, Python & React.
        </div>
      </div>
    </footer>
  );
}
