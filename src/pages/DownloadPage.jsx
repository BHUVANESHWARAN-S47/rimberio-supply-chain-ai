import React, { useState } from 'react';
import { Download, Archive, CheckCircle, Code2, Layers, Globe, Bot, FileText } from 'lucide-react';
import { exportProjectAsZip } from '../utils/exportProject';

export const DownloadPage = () => {
  const [downloading, setDownloading] = useState(false);
  const [done, setDone] = useState(false);

  const handleDownload = async () => {
    setDownloading(true);
    try {
      await exportProjectAsZip();
      setDone(true);
    } catch (e) {
      console.error(e);
    }
    setDownloading(false);
  };

  const contents = [
    {
      icon: Code2,
      label: 'Full React / Vite Source Code',
      desc: 'All JSX components, context, pages, utilities',
    },
    {
      icon: Layers,
      label: 'Design System (index.css)',
      desc: 'Earthy palette tokens, UI utilities, animations',
    },
    { icon: Globe, label: 'Tailwind Config & PostCSS', desc: 'Build pipeline configuration' },
    {
      icon: Bot,
      label: 'AI Agent Simulation Logic',
      desc: 'Negotiation engine, simulation state machines',
    },
    {
      icon: FileText,
      label: 'Package.json & README',
      desc: 'Dependency manifest and documentation',
    },
  ];

  return (
    <div className="space-y-5 pb-12">
      <div
        className="p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4"
        style={{
          background: '#FFFFFF',
          border: '1px solid rgba(240, 171, 252, 0.45)',
        }}
      >
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="badge badge-warning">FULL SOURCE CODE</span>
          </div>
          <h1 className="text-2xl md:text-3xl" style={{ color: 'var(--color-taupe)' }}>
            DOWNLOAD REACT SOURCE CODE
          </h1>
          <p className="text-xs mt-1" style={{ color: 'var(--color-mid)' }}>
            Export the complete RIMBERIO platform as a ready-to-deploy Vite + React ZIP archive.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        <div className="lg:col-span-7 rim-card p-6 space-y-5">
          <h2
            className="text-sm font-black uppercase tracking-widest"
            style={{ color: 'var(--color-taupe)', fontSize: '0.7rem', letterSpacing: '0.12em' }}
          >
            ARCHIVE CONTENTS
          </h2>
          <div className="space-y-3">
            {contents.map(({ icon: Icon, label, desc }) => (
              <div
                key={label}
                className="flex items-center gap-4 p-4 rounded-xl"
                style={{
                  background: 'var(--color-cream)',
                  border: '1px solid rgba(164,154,135,0.3)',
                }}
              >
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
                  style={{
                    background:
                      'linear-gradient(135deg, rgba(164,154,135,0.25), rgba(165,165,141,0.2))',
                  }}
                >
                  <Icon className="w-5 h-5" style={{ color: 'var(--color-sand)' }} />
                </div>
                <div>
                  <p className="text-sm font-bold" style={{ color: 'var(--color-dark)' }}>
                    {label}
                  </p>
                  <p className="text-xs" style={{ color: 'var(--color-mid)' }}>
                    {desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="lg:col-span-5 rim-card p-6 flex flex-col justify-between">
          <div>
            <h2
              className="text-sm font-black uppercase tracking-widest mb-4"
              style={{ color: 'var(--color-taupe)', fontSize: '0.7rem', letterSpacing: '0.12em' }}
            >
              DEPLOYMENT PACKAGE
            </h2>

            {[
              ['Platform', 'Vite 5 + React 18'],
              ['Styling', 'Tailwind CSS v3 + PostCSS'],
              ['Icons', 'Lucide React'],
              ['Font', 'Nunito (Lemon Milk style)'],
              ['Bundle Size', '~4.2 MB (source)'],
              ['License', 'MIT Enterprise'],
            ].map(([k, v]) => (
              <div
                key={k}
                className="flex justify-between text-xs py-2"
                style={{ borderBottom: '1px solid rgba(164,154,135,0.2)' }}
              >
                <span style={{ color: 'var(--color-mid)' }}>{k}</span>
                <span className="rim-mono font-bold" style={{ color: 'var(--color-dark)' }}>
                  {v}
                </span>
              </div>
            ))}
          </div>

          <div className="mt-6">
            {done ? (
              <div
                className="p-4 rounded-xl flex items-center gap-3 mb-4"
                style={{ background: '#D9EDDE', border: '1px solid #B7D9C0' }}
              >
                <CheckCircle className="w-5 h-5 text-green-700 shrink-0" />
                <p className="text-sm font-bold text-green-900">
                  Archive downloaded! Check your Downloads folder.
                </p>
              </div>
            ) : null}

            <button
              onClick={handleDownload}
              disabled={downloading}
              className="rim-btn-primary w-full flex items-center justify-center gap-3 text-sm py-4"
            >
              <Archive className={`w-5 h-5 ${downloading ? 'animate-spin' : ''}`} />
              {downloading ? 'Building ZIP Archive...' : 'Download rimberio-source.zip'}
            </button>

            <p className="text-center text-xs mt-3" style={{ color: 'var(--color-mid)' }}>
              Includes all pages, components, context, CSS, and build config
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
