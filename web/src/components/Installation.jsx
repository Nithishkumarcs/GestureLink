import React, { useState } from 'react';
import { Copy, Check, Terminal, Play, CheckCircle } from 'lucide-react';

export default function Installation({ repoUrl }) {
  const [copiedId, setCopiedId] = useState(null);

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const steps = [
    {
      id: 'step1',
      title: '1. Clone Repository & Navigate',
      cmd: `git clone ${repoUrl}.git\ncd GestureLink`
    },
    {
      id: 'step2',
      title: '2. Install Python Dependencies',
      cmd: `pip install -r requirements.txt`
    },
    {
      id: 'step3',
      title: '3. Run Desktop Application',
      cmd: `# Launch via Python:\npython main.py\n\n# Or double-click in Windows Explorer:\nrun.bat`
    },
    {
      id: 'step4',
      title: '4. Run Automated 12-Stage Test Suite (Optional)',
      cmd: `python test_system.py`
    },
    {
      id: 'step5',
      title: '5. Run This Web Frontend (Development)',
      cmd: `cd web\nnpm install\nnpm run dev`
    }
  ];

  return (
    <section id="install" className="section" style={{ background: 'rgba(11, 15, 25, 0.4)' }}>
      <div className="container">
        <div className="section-header">
          <div className="section-tag">Quickstart Guide</div>
          <h2 className="section-title">Install & Run GestureLink</h2>
          <p className="section-subtitle">
            Get up and running in under 2 minutes. Requires Python 3.10+ and a standard laptop webcam.
          </p>
        </div>

        <div className="install-container">
          {steps.map((step) => (
            <div key={step.id} className="code-window">
              <div className="code-header">
                <span className="code-title">{step.title}</span>
                <button
                  className="copy-btn"
                  onClick={() => copyToClipboard(step.cmd, step.id)}
                  title="Copy command to clipboard"
                >
                  {copiedId === step.id ? (
                    <>
                      <Check size={14} style={{ color: '#10b981' }} /> Copied!
                    </>
                  ) : (
                    <>
                      <Copy size={14} /> Copy
                    </>
                  )}
                </button>
              </div>
              <pre className="code-content">
                <code>{step.cmd}</code>
              </pre>
            </div>
          ))}

          {/* Quick Hardware Checklist */}
          <div style={{ marginTop: '36px', padding: '24px', background: 'rgba(18, 24, 38, 0.6)', borderRadius: '16px', border: '1px solid rgba(56, 189, 248, 0.15)' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '14px', color: '#f8fafc' }}>
              Minimum System Requirements:
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', fontSize: '0.88rem', color: '#94a3b8' }}>
              <div>✔ <strong>OS:</strong> Windows 10 / 11</div>
              <div>✔ <strong>Camera:</strong> 720p or 480p standard webcam</div>
              <div>✔ <strong>RAM:</strong> 4GB minimum</div>
              <div>✔ <strong>CPU:</strong> Intel i3 / AMD Ryzen 3 or higher</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
