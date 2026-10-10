import React, { useState } from 'react';
import { 
  MousePointer, 
  PenTool, 
  Tv, 
  Rocket, 
  Presentation,
  CheckCircle,
  Sparkles,
  Sliders
} from 'lucide-react';

export default function ModesShowcase() {
  const [activeTab, setActiveTab] = useState('mouse');

  const modesData = {
    mouse: {
      id: 'mouse',
      icon: <MousePointer size={18} />,
      title: 'Mouse Control Mode',
      tagline: 'Sub-millimeter cursor precision with jitter-free smoothing',
      desc: 'Controls your Windows desktop pointer completely touchless. Coordinates from the index fingertip are calibrated within an interaction bounding box and processed using adaptive Exponential Moving Average (EMA). Tiny tremor movements are filtered with deadzones, while quick sweeps remain snappy and responsive.',
      highlights: [
        'Adaptive EMA Smoothing factor (configurable 0.10 to 0.95)',
        'Interaction box mapping re-scales comfortable arm span to full monitor resolution',
        'Pinch gesture produces single left click (short tap) or drag-and-drop (sustained hold)',
        'Two fingers vertical movement drives buttery-smooth page and document scrolling',
        'OK gesture triggers instant double-click with cooldown protection'
      ],
      gestureMap: [
        { gesture: '☝️ Index Finger', result: 'Move cursor across screen' },
        { gesture: '🤏 Pinch Tap', result: 'Single Left Click' },
        { gesture: '🤏 Pinch Hold', result: 'Mouse Down (Drag & Drop)' },
        { gesture: '✌️ Two Fingers', result: 'Scroll Wheel (Up / Down)' },
        { gesture: '👌 OK Sign', result: 'Double Click' }
      ]
    },
    airwriting: {
      id: 'airwriting',
      icon: <PenTool size={18} />,
      title: '3D Air Writing',
      tagline: 'Vibrant neon drawing strokes floating directly in the air',
      desc: 'Write equations, annotate live camera feeds, or sketch signatures directly in the air. As your index fingertip moves, high-speed stroke interpolation draws continuous glowing lines with zero disjointed points. Features an eraser gesture, color palette cycle, and export to PNG.',
      highlights: [
        'Anti-aliased neon brush with configurable stroke thickness',
        'Multi-color palette cycling: Cyan, Emerald Green, Neon Yellow, Purple, Crimson',
        'Two-finger spatial eraser clears strokes dynamically within proximity radius',
        'Lifting hand or open palm automatically lifts virtual pen without drawing unwanted lines',
        'Export drawings directly to local high-resolution PNG image files'
      ],
      gestureMap: [
        { gesture: '☝️ Index Finger', result: 'Draw active color stroke' },
        { gesture: '🖐️ Open Palm', result: 'Lift pen (Hover without drawing)' },
        { gesture: '✌️ Two Fingers', result: 'Spatial eraser at fingertip' },
        { gesture: '🤏 Pinch Tap', result: 'Cycle pen color palette' },
        { gesture: 'Button Click', result: 'Save PNG / Clear canvas' }
      ]
    },
    whiteboard: {
      id: 'whiteboard',
      icon: <Tv size={18} />,
      title: 'Virtual Whiteboard',
      tagline: 'Dedicated 1280x720 clean digital slate for teaching & meetings',
      desc: 'Opens an independent high-resolution whiteboard window for presentations, virtual tutoring, brainstorming, and software architecture diagrams. Keeps your live camera feed separate while translating your hand gestures onto the clean digital slate.',
      highlights: [
        'Dedicated 1280x720 canvas rendering at full screen clarity',
        'Separate desktop window controllable without obstructing your desktop workspace',
        'Real-time gesture undo stack to revert accidental marks',
        'Dual-mode pen and precision eraser',
        'Direct export capability for meeting notes and lecture summaries'
      ],
      gestureMap: [
        { gesture: '☝️ Index Finger', result: 'Sketch strokes on whiteboard' },
        { gesture: '✌️ Two Fingers', result: 'Erase whiteboard markings' },
        { gesture: '🖐️ Open Palm', result: 'Hover cursor without ink' },
        { gesture: 'Toolbar / Key', result: 'Undo / Clear / Export PNG' }
      ]
    },
    launcher: {
      id: 'launcher',
      icon: <Rocket size={18} />,
      title: 'Application Launcher',
      tagline: 'Touchless circular menu to browse and execute Windows software',
      desc: 'Navigate and launch your favorite Windows utilities without reaching for the keyboard or start menu. Uses two-finger cycling to browse the application list, thumb-up to launch, and thumb-down to dismiss safely.',
      highlights: [
        'Pre-configured presets: Notepad, Calculator, File Explorer, Web Browser, Paint, Task Manager',
        'Fully customizable via settings.json: add custom executable paths, scripts, or URLs',
        'Non-blocking background process spawning with error notification popups',
        'Visual icon badges with instant feedback on current selection'
      ],
      gestureMap: [
        { gesture: '✌️ Two Fingers', result: 'Select next application in menu' },
        { gesture: '👍 Thumb Up', result: 'Execute / Launch selected application' },
        { gesture: '👎 Thumb Down', result: 'Cancel and return to Mouse Control' }
      ]
    },
    presentation: {
      id: 'presentation',
      icon: <Presentation size={18} />,
      title: 'Presentation Controller',
      tagline: 'Navigate PowerPoint, Google Slides, and PDFs with gestures',
      desc: 'Designed for conference speakers, lecturers, and remote meetings. GestureLink detects rapid horizontal hand swipes to turn slides forward or backward, and supports starting slideshows (F5) or exiting (ESC) touchless from across the room.',
      highlights: [
        'Swipe velocity filter detects natural directional hand flicks',
        'Universal compatibility with PowerPoint, Google Slides, Adobe Acrobat, and Keynote',
        'Debounced slide triggers prevent accidental multi-slide skipping',
        'Works comfortably from up to 3 meters away with standard webcams'
      ],
      gestureMap: [
        { gesture: '👉 Horizontal Swipe Right', result: 'Next Slide (Page Down / Right Arrow)' },
        { gesture: '👈 Horizontal Swipe Left', result: 'Previous Slide (Page Up / Left Arrow)' },
        { gesture: '👍 Thumb Up', result: 'Start Slideshow (F5)' },
        { gesture: '✊ Fist / 👎 Thumb Down', result: 'Exit Slideshow (ESC)' }
      ]
    }
  };

  const currentMode = modesData[activeTab];

  return (
    <section id="modes" className="section">
      <div className="container">
        <div className="section-header">
          <div className="section-tag">Dedicated Workspaces</div>
          <h2 className="section-title">5 Specialized Control Modes</h2>
          <p className="section-subtitle">
            Switch effortlessly between everyday desktop navigation, air sketching, digital whiteboards, app launching, and slide presentations.
          </p>
        </div>

        {/* Tab Buttons */}
        <div className="modes-tab-container">
          {Object.values(modesData).map((m) => (
            <button
              key={m.id}
              className={`tab-btn ${activeTab === m.id ? 'active' : ''}`}
              onClick={() => setActiveTab(m.id)}
            >
              {m.icon}
              <span>{m.title.replace(' Mode', '')}</span>
            </button>
          ))}
        </div>

        {/* Mode Detail Card */}
        <div className="mode-detail-card">
          <div className="mode-info-col">
            <h3 className="mode-info-title">{currentMode.title}</h3>
            <p style={{ color: '#00e5ff', fontSize: '0.95rem', fontWeight: 600, marginBottom: '14px' }}>
              {currentMode.tagline}
            </p>
            <p className="mode-info-desc">{currentMode.desc}</p>

            <div style={{ marginBottom: '24px' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', marginBottom: '12px' }}>
                Key Technical Highlights:
              </div>
              <div className="mode-specs-list">
                {currentMode.highlights.map((h, i) => (
                  <div key={i} className="mode-spec-item">
                    <CheckCircle size={16} className="mode-spec-bullet" style={{ flexShrink: 0, marginTop: '3px' }} />
                    <span>{h}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Visual Gesture Mapping Box */}
          <div className="mode-visual-box">
            <div style={{ fontSize: '0.8rem', fontWeight: 700, letterSpacing: '0.08em', color: '#38bdf8', marginBottom: '16px', textTransform: 'uppercase' }}>
              Active Gesture Mapping for {currentMode.title}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {currentMode.gestureMap.map((mapItem, idx) => (
                <div 
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px 16px',
                    background: 'rgba(15, 23, 42, 0.7)',
                    borderRadius: '10px',
                    border: '1px solid rgba(255, 255, 255, 0.06)'
                  }}
                >
                  <span style={{ fontWeight: 600, fontSize: '0.9rem', color: '#f8fafc' }}>
                    {mapItem.gesture}
                  </span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem', color: '#00e5ff' }}>
                    &rarr; {mapItem.result}
                  </span>
                </div>
              ))}
            </div>

            <div style={{ marginTop: '20px', padding: '12px', background: 'rgba(0, 229, 255, 0.05)', borderRadius: '8px', border: '1px dashed rgba(0, 229, 255, 0.2)', fontSize: '0.8rem', color: '#94a3b8' }}>
              Switch modes on the desktop dashboard via sidebar buttons or keyboard shortcuts anytime.
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
