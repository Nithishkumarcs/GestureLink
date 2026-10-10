import React, { useState, useEffect } from 'react';
import { Sparkles, RefreshCw, AlertCircle, ShieldAlert } from 'lucide-react';

export default function InteractiveSimulator() {
  const [selectedGesture, setSelectedGesture] = useState('INDEX_FINGER');
  const [cursorPos, setCursorPos] = useState({ x: 260, y: 140 });
  const [stability, setStability] = useState(100);
  const [emergencyStop, setEmergencyStop] = useState(false);
  const [actionDesc, setActionDesc] = useState('Moving Cursor');

  const gestureOptions = [
    { key: 'INDEX_FINGER', label: '☝️ Index Finger', action: 'Moving Cursor' },
    { key: 'PINCH', label: '🤏 Pinch', action: 'Left Click (Holding Drag)' },
    { key: 'TWO_FINGERS', label: '✌️ Two Fingers', action: 'Scrolling Screen (Up/Down)' },
    { key: 'OK_GESTURE', label: '👌 OK Sign', action: 'Double Click Triggered' },
    { key: 'OPEN_PALM', label: '🖐️ Open Palm', action: 'Neutral Idle (Safe)' },
    { key: 'FIST', label: '✊ Fist', action: 'Pause / Fullscreen Toggle' },
    { key: 'THUMB_UP', label: '👍 Thumb Up', action: 'Confirm / Launch Application' }
  ];

  const handleMouseMove = (e) => {
    if (emergencyStop) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = Math.round(e.clientX - rect.left);
    const y = Math.round(e.clientY - rect.top);
    setCursorPos({ x, y });
  };

  const selectGesture = (gesture) => {
    setSelectedGesture(gesture.key);
    setActionDesc(emergencyStop ? 'AUTOMATION LOCKED' : gesture.action);
    setStability(30);
    // Animate stability fill
    setTimeout(() => setStability(70), 100);
    setTimeout(() => setStability(100), 220);
  };

  const toggleEmergencyStop = () => {
    const nextState = !emergencyStop;
    setEmergencyStop(nextState);
    setActionDesc(nextState ? 'EMERGENCY STOPPED - AUTOMATION LOCKED' : 'System Resumed');
  };

  return (
    <section id="simulator" className="section" style={{ background: 'rgba(7, 10, 18, 0.7)' }}>
      <div className="container">
        <div className="section-header">
          <div className="section-tag">Hands-On Web Demo</div>
          <h2 className="section-title">Interactive Gesture Simulator</h2>
          <p className="section-subtitle">
            Experience how GestureLink’s stability tracker and landmark projection pipeline process 
            spatial coordinates inside the browser canvas.
          </p>
        </div>

        <div className="simulator-box">
          {/* Top HUD Bar */}
          <div className="sim-hud">
            <div>
              <span style={{ color: '#64748b' }}>TRACKER: </span>
              <span style={{ color: emergencyStop ? '#ef4444' : '#00e5ff' }}>
                {emergencyStop ? 'LOCKED (ESC)' : '21 3D LANDMARKS (ACTIVE)'}
              </span>
            </div>
            <div>
              <span style={{ color: '#64748b' }}>COORDINATES: </span>
              <span style={{ color: '#38bdf8' }}>X: {cursorPos.x}px | Y: {cursorPos.y}px</span>
            </div>
            <div>
              <span style={{ color: '#64748b' }}>CONFIDENCE: </span>
              <span style={{ color: '#10b981' }}>98.4%</span>
            </div>
          </div>

          {/* Interactive Canvas Area */}
          <div 
            className="sim-canvas" 
            onMouseMove={handleMouseMove}
            style={{ cursor: emergencyStop ? 'not-allowed' : 'crosshair' }}
          >
            {/* Grid Lines */}
            <div style={{ position: 'absolute', inset: 0, backgroundImage: 'radial-gradient(rgba(0, 229, 255, 0.15) 1px, transparent 1px)', backgroundSize: '24px 24px' }}></div>

            {/* Interaction Box Bounds */}
            <div style={{
              position: 'absolute',
              width: '80%',
              height: '75%',
              border: emergencyStop ? '1px dashed #ef4444' : '1px dashed #00e5ff',
              borderRadius: '12px',
              pointerEvents: 'none'
            }}>
              <div style={{
                position: 'absolute',
                top: '10px',
                left: '12px',
                color: emergencyStop ? '#ef4444' : '#00e5ff',
                fontSize: '0.75rem',
                fontFamily: 'var(--font-mono)'
              }}>
                [INTERACTION ZONE] Move mouse inside to simulate hand tracking
              </div>
            </div>

            {/* Simulated Fingertip Node */}
            <div 
              style={{
                position: 'absolute',
                left: `${cursorPos.x - 10}px`,
                top: `${cursorPos.y - 10}px`,
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                background: emergencyStop ? '#ef4444' : '#00e5ff',
                boxShadow: emergencyStop ? '0 0 20px #ef4444' : '0 0 24px #00e5ff',
                transition: 'box-shadow 0.2s',
                pointerEvents: 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#fff' }}></div>

              {/* Tag Callout */}
              <div style={{
                position: 'absolute',
                top: '-30px',
                left: '20px',
                background: '#0f172a',
                border: `1px solid ${emergencyStop ? '#ef4444' : '#00e5ff'}`,
                color: emergencyStop ? '#ef4444' : '#00e5ff',
                fontSize: '0.72rem',
                fontFamily: 'var(--font-mono)',
                padding: '2px 8px',
                borderRadius: '4px',
                whiteSpace: 'nowrap'
              }}>
                {selectedGesture}
              </div>
            </div>

            {/* Real-Time Action Floating Pill */}
            <div style={{
              position: 'absolute',
              bottom: '16px',
              padding: '8px 20px',
              borderRadius: '9999px',
              background: 'rgba(15, 23, 42, 0.85)',
              border: `1px solid ${emergencyStop ? '#ef4444' : '#10b981'}`,
              color: emergencyStop ? '#ef4444' : '#10b981',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.88rem',
              fontWeight: 600,
              boxShadow: '0 4px 16px rgba(0,0,0,0.5)'
            }}>
              ACTION: {actionDesc}
            </div>
          </div>

          {/* Stability Bar */}
          <div style={{ marginTop: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '6px', color: '#94a3b8' }}>
              <span>Temporal Stability Verification:</span>
              <span style={{ color: '#00e5ff', fontFamily: 'var(--font-mono)' }}>{stability}% (4 Frames Verified)</span>
            </div>
            <div style={{ height: '8px', background: '#1e293b', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{
                width: `${stability}%`,
                height: '100%',
                background: emergencyStop ? '#ef4444' : 'linear-gradient(90deg, #0284c7, #00e5ff)',
                transition: 'width 0.2s cubic-bezier(0.16, 1, 0.3, 1)'
              }}></div>
            </div>
          </div>

          {/* Gesture Switcher Buttons */}
          <div className="sim-controls">
            {gestureOptions.map((g) => (
              <button
                key={g.key}
                className={`sim-btn ${selectedGesture === g.key ? 'active' : ''}`}
                onClick={() => selectGesture(g)}
              >
                {g.label}
              </button>
            ))}

            <button
              onClick={toggleEmergencyStop}
              style={{
                padding: '8px 18px',
                fontSize: '0.85rem',
                fontWeight: 700,
                borderRadius: '9999px',
                background: emergencyStop ? '#10b981' : '#dc2626',
                border: 'none',
                color: '#fff',
                cursor: 'pointer',
                transition: 'var(--transition)'
              }}
            >
              {emergencyStop ? 'Resume Automation' : '🛑 Emergency Stop (ESC)'}
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
