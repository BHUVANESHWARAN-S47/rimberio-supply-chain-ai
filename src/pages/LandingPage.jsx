import React, { useRef, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import {
  Cpu,
  ArrowRight,
  Bot,
  Sliders,
  Zap,
  ShieldCheck,
  ChevronDown,
  Globe2,
  TrendingDown,
  Activity,
  Layers,
} from 'lucide-react';

export const LandingPage = () => {
  const { setCurrentPage } = useApp();
  const videoRef = useRef(null);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.play().catch(() => {});
    }
  }, []);

  const corePillars = [
    {
      icon: Bot,
      tag: 'Multi-Agent AI',
      title: 'Bilateral Automated Negotiation',
      desc: 'Buyer and Supplier agents autonomously evaluate concession frontiers across unit cost, batch volume, and delivery schedules without manual overhead.',
    },
    {
      icon: Sliders,
      tag: 'Digital Twin',
      title: 'Counterfactual Disruption Sim',
      desc: '1,000-trial Monte Carlo simulations quantifying maritime bottlenecks, port wait times, and downstream inventory depletion risk.',
    },
    {
      icon: Zap,
      tag: 'Adaptive Engine',
      title: 'ML Decision & Switching Policy',
      desc: 'Trained Random Forest classification dynamically recommending whether to Retain incumbents, Negotiate terms, or Switch suppliers.',
    },
    {
      icon: ShieldCheck,
      tag: 'Enterprise SLA',
      title: 'Customer SLA Protection',
      desc: 'Real-time telemetry continuously computes tier-based penalty exposure, issues transparent advisories, and eliminates supply chain downtime.',
    },
  ];

  return (
    <div className="w-full min-h-screen bg-slate-950 text-white font-sans antialiased selection:bg-[#8e3a59] selection:text-white">
      {/* ── FULL-SCREEN HERO WITH EDGE-TO-EDGE VIDEO ── */}
      <div className="relative w-full min-h-screen flex flex-col justify-between overflow-hidden">
        {/* Full Bleed Background Video */}
        <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
          <video
            ref={videoRef}
            autoPlay
            loop
            muted
            playsInline
            className="w-full h-full object-cover opacity-60 filter brightness-90 contrast-110 scale-105"
          >
            <source src="/bg-video.mp4" type="video/mp4" />
          </video>
          {/* Subtle vignette & contrast overlay */}
          <div className="absolute inset-0 bg-gradient-to-b from-slate-950/80 via-slate-950/40 to-slate-950" />
        </div>

        {/* ── TRANSPARENT FIGMA-GRADE HEADER ── */}
        <header className="relative z-50 w-full px-6 lg:px-16 py-5 flex items-center justify-between border-b border-white/10 backdrop-blur-md bg-slate-950/30">
          <div
            className="flex items-center gap-3 cursor-pointer group"
            onClick={() => setCurrentPage('landing')}
          >
            <div className="w-9 h-9 rounded-lg bg-[#8e3a59] flex items-center justify-center text-white shadow-lg shadow-[#8e3a59]/30 group-hover:scale-105 transition-transform">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-sm tracking-tight text-white block leading-tight">
                RIMBERIO AI
              </span>
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-widest block">
                Supply Chain Twin
              </span>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-8 text-xs font-semibold uppercase tracking-wider text-slate-300">
            <button
              onClick={() => setCurrentPage('dashboard')}
              className="hover:text-white transition-colors"
            >
              Intelligence Map
            </button>
            <button
              onClick={() => setCurrentPage('simulation')}
              className="hover:text-white transition-colors"
            >
              Simulation Twin
            </button>
            <button
              onClick={() => setCurrentPage('negotiation')}
              className="hover:text-white transition-colors"
            >
              Multi-Agent Engine
            </button>
          </nav>

          <div className="flex items-center gap-4">
            <button
              onClick={() => setCurrentPage('login')}
              className="text-xs font-semibold text-slate-200 hover:text-white transition-colors px-3 py-2"
            >
              Sign In
            </button>
            <button
              onClick={() => setCurrentPage('register')}
              className="px-4 py-2 rounded-lg bg-[#8e3a59] hover:bg-[#752d48] text-white text-xs font-semibold shadow-md shadow-[#8e3a59]/40 hover:shadow-lg transition-all flex items-center gap-1.5"
            >
              Register
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </header>

        {/* ── CENTER HERO CONTENT ── */}
        <main className="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-6 max-w-5xl mx-auto my-auto py-12">
          {/* Live Runtime Pill */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-slate-200 text-xs font-medium mb-6 shadow-sm">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="tracking-wide">Enterprise Multi-Agent Runtime Active</span>
          </div>

          {/* Master Headline */}
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold text-white tracking-tight leading-[1.08] mb-6 drop-shadow-md">
            Autonomous AI <br className="hidden sm:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-pink-300 via-rose-200 to-white">
              Supply Chain Twin
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-base sm:text-lg lg:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed mb-10 font-normal">
            Predictive logistics delay forecasting, bilateral multi-agent vendor negotiation, and real-time counterfactual simulation for enterprise networks.
          </p>

          {/* Action Button Row */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 w-full sm:w-auto">
            <button
              onClick={() => setCurrentPage('register')}
              className="w-full sm:w-auto px-8 py-4 rounded-lg bg-[#8e3a59] hover:bg-[#752d48] text-white text-sm font-semibold shadow-xl shadow-[#8e3a59]/40 hover:shadow-2xl transition-all flex items-center justify-center gap-2"
            >
              Register Organization
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => setCurrentPage('login')}
              className="w-full sm:w-auto px-8 py-4 rounded-lg bg-white/10 hover:bg-white/20 text-white text-sm font-semibold border border-white/20 backdrop-blur-md transition-all flex items-center justify-center"
            >
              Sign In to Platform
            </button>
          </div>
        </main>

        {/* ── BOTTOM HERO BAR ── */}
        <div className="relative z-10 w-full px-6 lg:px-16 py-6 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400">
          <div className="flex items-center gap-6">
            <span className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-emerald-400" />
              Real-Time AIS Vessel Telemetry
            </span>
            <span className="hidden md:inline-flex items-center gap-2">
              <Layers className="w-4 h-4 text-[#8e3a59]" />
              5 Autonomous Agent Roles
            </span>
          </div>

          <a
            href="#capabilities"
            className="flex items-center gap-1.5 text-slate-400 hover:text-white transition-colors"
          >
            <span>Explore Core Capabilities</span>
            <ChevronDown className="w-4 h-4 animate-bounce" />
          </a>
        </div>
      </div>

      {/* ── CORE CAPABILITIES SECTION (CLEAN FIGMA-STYLE GRID) ── */}
      <section id="capabilities" className="w-full py-24 bg-white text-slate-900 border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-6 lg:px-16">
          <div className="max-w-3xl mx-auto text-center mb-16">
            <span className="text-xs font-bold uppercase tracking-widest text-[#8e3a59] block mb-2">
              Production Architecture
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight mb-4">
              Core Platform Capabilities
            </h2>
            <p className="text-base text-slate-600 leading-relaxed">
              Designed for enterprise operations to eliminate logistics bottlenecks, automate supplier contracts, and safeguard production schedules.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {corePillars.map((p) => {
              const Icon = p.icon;
              return (
                <div
                  key={p.title}
                  className="p-7 rounded-xl bg-slate-50 border border-slate-200 hover:border-slate-300 hover:shadow-lg transition-all flex flex-col justify-between group"
                >
                  <div>
                    <div className="w-12 h-12 rounded-lg bg-white border border-slate-200 flex items-center justify-center text-[#8e3a59] shadow-sm mb-5 group-hover:scale-105 transition-transform">
                      <Icon className="w-6 h-6" />
                    </div>
                    <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400 block mb-1">
                      {p.tag}
                    </span>
                    <h3 className="text-base font-bold text-slate-900 mb-2 leading-snug">
                      {p.title}
                    </h3>
                    <p className="text-xs text-slate-600 leading-relaxed">
                      {p.desc}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Quick CTA strip */}
          <div className="mt-16 p-8 rounded-xl bg-slate-900 text-white flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl">
            <div>
              <h3 className="text-lg font-bold mb-1">
                Experience the Autonomous Multi-Agent Console
              </h3>
              <p className="text-xs text-slate-400">
                Calibrated against Kaggle supply chain datasets with trained Gradient Boosting and Random Forest models.
              </p>
            </div>
            <div className="flex items-center gap-3 shrink-0">
              <button
                onClick={() => setCurrentPage('register')}
                className="px-6 py-3 rounded-lg bg-[#8e3a59] hover:bg-[#752d48] text-white text-xs font-semibold shadow-md transition-all"
              >
                Register Organization
              </button>
              <button
                onClick={() => setCurrentPage('dashboard')}
                className="px-6 py-3 rounded-lg bg-white/10 hover:bg-white/20 text-white text-xs font-semibold border border-white/20 transition-all"
              >
                View Live Map
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* ── MINIMAL FOOTER ── */}
      <footer className="w-full py-8 bg-slate-950 text-slate-500 text-xs border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-6 lg:px-16 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-300">RIMBERIO AI</span>
            <span>—</span>
            <span>Enterprise Digital Supply Chain Twin</span>
          </div>
          <div className="flex items-center gap-4 text-xs">
            <span className="inline-flex items-center gap-1.5 text-emerald-400 font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              All Systems Operational
            </span>
            <span>© 2026 Rimberio Platform</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
