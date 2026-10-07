import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { Cpu, Mail, Lock, User, Building2, ArrowRight, Eye, EyeOff, CheckCircle2 } from 'lucide-react';

export const RegisterPage = () => {
  const { login, setCurrentPage } = useApp();
  const [form, setForm] = useState({
    name: 'Elena Rostova',
    email: 'elena.rostova@rimberio.ai',
    company: 'Apex Dynamics Corp',
    role: 'Procurement Director',
    password: 'enterprise_pass_2026',
  });
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);

  const update = (k, v) => setForm((prev) => ({ ...prev, [k]: v }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    await new Promise((r) => setTimeout(r, 600));
    login(form.email || 'user@rimberio.ai', form.password);
    setLoading(false);
  };

  return (
    <div className="w-full min-h-screen flex flex-col lg:flex-row bg-white font-sans antialiased">
      {/* ── LEFT 50%: FULL-SCREEN ENTERPRISE BRAND & VALUE PANEL ── */}
      <div className="w-full lg:w-1/2 min-h-[420px] lg:min-h-screen bg-slate-950 p-8 sm:p-12 lg:p-20 flex flex-col justify-between text-white relative overflow-hidden">
        {/* Subtle background ambient gradients */}
        <div className="absolute top-0 -left-20 w-96 h-96 rounded-full bg-[#8e3a59]/30 blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 right-0 w-80 h-80 rounded-full bg-slate-800/40 blur-3xl pointer-events-none" />

        {/* Brand Header */}
        <div
          className="relative z-10 flex items-center gap-3 cursor-pointer group"
          onClick={() => setCurrentPage('landing')}
        >
          <div className="w-10 h-10 rounded-lg bg-[#8e3a59] flex items-center justify-center text-white shadow-lg shadow-[#8e3a59]/40 group-hover:scale-105 transition-transform">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <span className="font-bold text-base tracking-tight text-white block leading-tight">
              RIMBERIO AI
            </span>
            <span className="text-[11px] font-mono text-slate-400 uppercase tracking-widest block">
              Digital Twin Platform
            </span>
          </div>
        </div>

        {/* Center Showcase */}
        <div className="relative z-10 my-auto py-8 max-w-lg">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/15 text-xs font-medium text-slate-200 mb-6">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Enterprise Onboarding &amp; Node Provisioning
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight leading-tight mb-4">
            Provision Your Supply Chain Twin Node
          </h1>

          <p className="text-sm sm:text-base text-slate-300 leading-relaxed mb-8 font-normal">
            Configure autonomous agents, connect real-time vessel telemetry, and simulate supplier contract variations.
          </p>

          <div className="space-y-4 pt-2">
            <div className="flex items-start gap-3 text-xs sm:text-sm text-slate-200">
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
              <span>Instant Buyer &amp; Supplier Agent Node Deployment</span>
            </div>
            <div className="flex items-start gap-3 text-xs sm:text-sm text-slate-200">
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
              <span>Pre-calibrated with 180,000+ Kaggle DataCo Trade Records</span>
            </div>
            <div className="flex items-start gap-3 text-xs sm:text-sm text-slate-200">
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
              <span>Continuous Maritime Chokepoint &amp; Port Congestion Ingestion</span>
            </div>
          </div>
        </div>

        {/* Security Badges */}
        <div className="relative z-10 pt-6 border-t border-slate-800 flex items-center justify-between text-xs font-mono text-slate-400">
          <span>SOC 2 TYPE II CERTIFIED</span>
          <span>AES-256 ENCRYPTION</span>
          <span>ISO 27001</span>
        </div>
      </div>

      {/* ── RIGHT 50%: FULL-SCREEN FORM PANEL ── */}
      <div className="w-full lg:w-1/2 min-h-screen bg-white p-8 sm:p-14 lg:p-20 flex flex-col justify-center items-center">
        <div className="w-full max-w-lg">
          <div className="mb-8">
            <span className="text-xs font-bold uppercase tracking-wider text-[#8e3a59] block mb-1">
              New Enterprise Deployment
            </span>
            <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
              Register Organization
            </h2>
            <p className="text-sm text-slate-500 mt-1.5 leading-relaxed">
              Create your corporate profile to provision the digital twin environment.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-2">
                  Full Name
                </label>
                <div className="relative">
                  <User className="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
                  <input
                    type="text"
                    value={form.name}
                    onChange={(e) => update('name', e.target.value)}
                    required
                    className="w-full h-11 pl-12 pr-4 rounded-lg border border-slate-300 text-sm text-slate-900 bg-white placeholder-slate-400 focus:outline-none focus:border-[#8e3a59] focus:ring-2 focus:ring-[#8e3a59]/20 transition-all"
                    placeholder="Elena Rostova"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-2">
                  Enterprise Name
                </label>
                <div className="relative">
                  <Building2 className="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
                  <input
                    type="text"
                    value={form.company}
                    onChange={(e) => update('company', e.target.value)}
                    required
                    className="w-full h-11 pl-12 pr-4 rounded-lg border border-slate-300 text-sm text-slate-900 bg-white placeholder-slate-400 focus:outline-none focus:border-[#8e3a59] focus:ring-2 focus:ring-[#8e3a59]/20 transition-all"
                    placeholder="Apex Dynamics"
                  />
                </div>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-2">
                Corporate Email
              </label>
              <div className="relative">
                <Mail className="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) => update('email', e.target.value)}
                  required
                  className="w-full h-11 pl-12 pr-4 rounded-lg border border-slate-300 text-sm text-slate-900 bg-white placeholder-slate-400 focus:outline-none focus:border-[#8e3a59] focus:ring-2 focus:ring-[#8e3a59]/20 transition-all"
                  placeholder="name@company.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-2">
                Security Key / Password
              </label>
              <div className="relative">
                <Lock className="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
                <input
                  type={showPass ? 'text' : 'password'}
                  value={form.password}
                  onChange={(e) => update('password', e.target.value)}
                  required
                  className="w-full h-11 pl-12 pr-12 rounded-lg border border-slate-300 text-sm text-slate-900 bg-white placeholder-slate-400 focus:outline-none focus:border-[#8e3a59] focus:ring-2 focus:ring-[#8e3a59]/20 transition-all"
                  placeholder="Create a strong password"
                />
                <button
                  type="button"
                  onClick={() => setShowPass(!showPass)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                >
                  {showPass ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full h-12 rounded-lg bg-[#8e3a59] hover:bg-[#752d48] text-white text-sm font-semibold shadow-md shadow-[#8e3a59]/30 hover:shadow-lg transition-all flex items-center justify-center gap-2 mt-4"
            >
              {loading ? (
                <span>Provisioning Twin Node...</span>
              ) : (
                <>
                  <span>Create Enterprise Account</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-slate-200 text-center space-y-3">
            <p className="text-sm text-slate-600">
              Already registered?{' '}
              <button
                onClick={() => setCurrentPage('login')}
                className="font-bold text-[#8e3a59] hover:underline ml-1"
              >
                Sign In
              </button>
            </p>

            <div>
              <button
                onClick={() => setCurrentPage('landing')}
                className="inline-flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-slate-900 transition-colors"
              >
                ← Back to Platform Overview
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
