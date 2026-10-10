import React from 'react';

export default function Gestures() {
  const gestures = [
    {
      emoji: '☝️',
      name: 'Index Finger',
      action: 'Move Cursor / Draw',
      target: 'Mouse & Air Writing',
      desc: 'Extends only the index finger. Maps fingertip coordinates with adaptive EMA smoothing to position the desktop cursor or draw color strokes in the air.'
    },
    {
      emoji: '🤏',
      name: 'Pinch (Thumb + Index)',
      action: 'Left Click / Drag',
      target: 'Mouse & Whiteboard',
      desc: 'Calculates Euclidean 2D distance between thumb tip and index fingertip. Quick tap generates a left-click; sustained pinch holds mouse button down for dragging.'
    },
    {
      emoji: '✌️',
      name: 'Two Fingers (Victory)',
      action: 'Vertical Scroll / Erase',
      target: 'Navigation & Tools',
      desc: 'Index and middle fingers extended. In Mouse Mode, vertical displacement drives smooth scrolling. In Air Writing, acts as a spatial eraser.'
    },
    {
      emoji: '👌',
      name: 'OK Gesture',
      action: 'Double Click',
      target: 'Desktop Navigation',
      desc: 'Forms a closed loop between thumb and index while keeping other fingers erect. Triggers debounced desktop double-click to open folders or apps.'
    },
    {
      emoji: '✊',
      name: 'Fist',
      action: 'Idle / Fullscreen (F11)',
      target: 'Safety & Presentation',
      desc: 'All fingers folded into palm. Safely pauses cursor movement and can toggle application fullscreen or exit slide show mode.'
    },
    {
      emoji: '🖐️',
      name: 'Open Palm',
      action: 'Neutral Idle / Hover',
      target: 'All Modes',
      desc: 'All 5 fingers extended. Represents the neutral safety state. Lifts virtual drawing pen in Air Writing and stops cursor drifting.'
    },
    {
      emoji: '👍',
      name: 'Thumb Up',
      action: 'Confirm / Launch / Start',
      target: 'App Launcher & Slides',
      desc: 'Thumb pointing upwards with fist closed. Executes selected Windows application in App Launcher or starts presentation in full-screen mode.'
    },
    {
      emoji: '👎',
      name: 'Thumb Down',
      action: 'Cancel / Back / Exit',
      target: 'App Launcher & Slides',
      desc: 'Thumb pointing downwards. Cancels application selection dialog or returns presentation mode back to default cursor navigation.'
    }
  ];

  return (
    <section id="gestures" className="section" style={{ background: 'rgba(11, 15, 25, 0.4)' }}>
      <div className="container">
        <div className="section-header">
          <div className="section-tag">Spatial Lexicon</div>
          <h2 className="section-title">8 Natural Hand Gestures</h2>
          <p className="section-subtitle">
            Engineered with rotation-invariant joint angle trigonometry and temporal validation for zero false triggers.
          </p>
        </div>

        <div className="gestures-grid">
          {gestures.map((g, idx) => (
            <div key={idx} className="gesture-card">
              <div className="gesture-emoji-box">{g.emoji}</div>
              <h3 className="gesture-name">{g.name}</h3>
              <div className="gesture-action-tag">{g.action}</div>
              <p className="gesture-detail">{g.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
