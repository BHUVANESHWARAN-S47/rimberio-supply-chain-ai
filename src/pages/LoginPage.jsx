import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import {
  Cpu,
  Mail,
  Lock,
  ArrowRight,
  Eye,
  EyeOff,
  CheckCircle2,
  AlertCircle,
  Shield,
  ShoppingBag,
  Truck,
  Building2,
  User,
  Sparkles,
} from 'lucide-react';

const DEMO_ACCOUNTS = [
  {
    role: 'Admin',
    name: 'Alexander Vance',
    email: 'admin@rimberio.ai',
    password: 'enterprise_pass_2026',
    badge: 'Enterprise IT',
    icon: Shield,
    color: 'border-slate-300 hover:border-slate-800 hover:bg-slate-50',
    tagColor: 'bg-slate-900 text-white',
  },
  {
    role: 'Buyer',
    name: 'Priya Sharma',
    email: 'buyer@rimberio.ai',
    password: 'enterprise_pass_2026',
    badge: 'Procurement',
    icon: ShoppingBag,
    color: 'border-rose-200 hover:border-[#8e3a59] hover:bg-rose-50/50',
    tagColor: 'bg-[#8e3a59] text-white',
  },
  {
    role: 'Logistics',
    name: 'Henrik Lindholm',
    email: 'logistics@rimberio.ai',
    password: 'enterprise_pass_2026',
    badge: 'Freight & Fleet',
    icon: Truck,
    color: 'border-amber-200 hover:border-amber-700 hover:bg-amber-50/50',
    tagColor: 'bg-amber-700 text-white',
  },
  {
    role: 'Supplier',
    name: 'Kenji Sato (Apex)',
    email: 'supplier@apexlogistics.com',
    password: 'enterprise_pass_2026',
    badge: 'Supplier Portal',
    icon: Building2,
    color: 'border-emerald-200 hover:border-emerald-700 hover:bg-emerald-50/50',
    tagColor: 'bg-emerald-700 text-white',
  },
  {
    role: 'Customer',
    name: 'Rachel Adams (Boeing)',
    email: 'customer@boeing.com',
    password: 'enterprise_pass_2026',
    badge: 'Client Portal',
    icon: User,
    color: 'border-purple-200 hover:border-purple-700 hover:bg-purple-50/50',
    tagColor: 'bg-purple-700 text-white',
  },
];

export const LoginPage = () => {
  const { login, setCurrentPage } = useApp();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [remember, setRemember] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      // login() in AppContext handles navigation to dashboard
    } catch (err) {
      if (err.message?.includes('Failed to fetch') || err.message?.includes('NetworkError')) {
        setError('Cannot connect to backend server (http://127.0.0.1:8000). Please start the backend with `npm run backend` or ensure Python is running.');
      } else {
        setError(err.message || 'Authentication failed. Please check your credentials.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSelectDemo = (demo) => {
    setEmail(demo.email);
    setPassword(demo.password);
    setError('');
  };



  return (
    <div className="w-full min-h-screen flex flex-col lg:flex-row bg-white font-sans antialiased">
      {/* ── LEFT: Brand Panel ── */}
      <div className="w-full lg:w-1/2 min-h-[420px] lg:min-h-screen bg-slate-950 p-8 sm:p-12 lg:p-20 flex flex-col justify-between text-white relative overflow-hidden">
        <div className="absolute top-0 -left-20 w-96 h-96 rounded-full bg-[#8e3a59]/30 blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 right-0 w-80 h-80 rounded-full bg-slate-800/40 blur-3xl pointer-events-none" />

        {/* Brand */}
        <div
          className="relative z-10 flex items-center gap-3 cursor-pointer group"
          onClick={() => setCurrentPage('landing')}
        >
          <div className="w-10 h-10 rounded-lg bg-[#8e3a59] flex items-center justify-center text-white shadow-lg shadow-[#8e3a59]/40 group-hover:scale-105 transition-transform">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <span className="font-bold text-base tracking-tight text-white block leading-tight">
              RIMBERIO
            </span>
            <span className="text-[11px] font-mono text-slate-400 uppercase tracking-widest block">
              Enterprise Supply Chain Platform
            </span>
          </div>
        </div>

        {/* Center */}
        <div className="relative z-10 my-auto py-8 max-w-lg">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/15 text-xs font-medium text-slate-200 mb-6">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Multi-Tenant Enterprise Platform
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight leading-tight mb-4">
            Enterprise Supply Chain Intelligence
          </h1>

          <p className="text-sm sm:text-base text-slate-300 leading-relaxed mb-8 font-normal">
            Sign in to access your department's workspace. Role-based dashboards, permissions, and AI capabilities are resolved automatically.
          </p>

          <div className="space-y-4 pt-2">
            <div className="flex items-start gap-3 text-xs sm:text-sm text-slate-200">
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
              <span>Role-specific dashboards for every department</span>
            </div>
            <div className="flex items-start gap-3 text-xs sm:text-sm text-slate-200">
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
              <span>AI-powered procurement, risk analysis &amp; negotiation</span>
            </div>
            <div className="flex items-start gap-3 text-xs sm:text-sm text-slate-200">
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
              <span>Multi-tenant isolation with enterprise-grade security</span>
            </div>
          </div>
        </div>

        {/* Footer badges */}
        <div className="relative z-10 pt-6 border-t border-slate-800 flex items-center justify-between text-xs font-mono text-slate-400">
          <span>RBAC ENFORCED</span>
          <span>JWT AUTHENTICATION</span>
          <span>TENANT ISOLATED</span>
        </div>
      </div>

      {/* ── RIGHT: Form Panel ── */}
      <div className="w-full lg:w-1/2 min-h-screen bg-white p-8 sm:p-14 lg:p-20 flex flex-col justify-center items-center">
        <div className="w-full max-w-lg">
          <div className="mb-8">
            <span className="text-xs font-bold uppercase tracking-wider text-[#8e3a59] block mb-1">
              Secure Enterprise Access
            </span>
            <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
              Sign In
            </h2>
            <p className="text-sm text-slate-500 mt-1.5 leading-relaxed">
              Enter your credentials to access your workspace.
            </p>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="mb-5 p-3 rounded-lg bg-red-50 border border-red-200 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
              <p className="text-xs font-medium text-red-700">{error}</p>
            </div>
          )}

          {/* Demo Login Shortcuts */}
          <div className="mb-6 p-4 rounded-xl bg-slate-50 border border-slate-200">
            <div className="flex items-center justify-between mb-2.5">
              <div className="flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-[#8e3a59]" />
                <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                  Demo Login Shortcuts
                </span>
              </div>
              <span className="text-[11px] font-mono text-slate-500">
                Key: <strong className="text-slate-700">enterprise_pass_2026</strong>
              </span>
            </div>
            <p className="text-[11px] text-slate-500 mb-2.5">
              Click any demo account to 1-click populate verified enterprise credentials:
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {DEMO_ACCOUNTS.map((demo) => {
                const Icon = demo.icon;
                const isSelected = email === demo.email;
                return (
                  <button
                    key={demo.role}
                    type="button"
                    onClick={() => handleSelectDemo(demo)}
                    className={`p-2.5 rounded-lg border text-left transition-all flex flex-col justify-between ${demo.color} ${
                      isSelected
                        ? 'ring-2 ring-[#8e3a59] border-[#8e3a59] bg-white shadow-sm'
                        : 'bg-white'
                    }`}
                  >
                    <div className="flex items-center justify-between w-full mb-1">
                      <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${demo.tagColor}`}>
                        {demo.role}
                      </span>
                      <Icon className="w-3.5 h-3.5 text-slate-400" />
                    </div>
                    <div className="text-[11px] font-semibold text-slate-900 truncate" title={demo.name}>
                      {demo.name}
                    </div>
                    <div className="text-[10px] font-mono text-slate-500 truncate" title={demo.email}>
                      {demo.email}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-2">
                Email
              </label>
              <div className="relative">
                <Mail className="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full h-12 pl-12 pr-4 rounded-lg border border-slate-300 text-sm text-slate-900 bg-white placeholder-slate-400 focus:outline-none focus:border-[#8e3a59] focus:ring-2 focus:ring-[#8e3a59]/20 transition-all"
                  placeholder="you@company.com"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700">
                  Password
                </label>
                <button
                  type="button"
                  onClick={() => setCurrentPage('forgot_password')}
                  className="text-xs font-medium text-[#8e3a59] hover:underline"
                >
                  Forgot Password?
                </button>
              </div>
              <div className="relative">
                <Lock className="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
                <input
                  type={showPass ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full h-12 pl-12 pr-12 rounded-lg border border-slate-300 text-sm text-slate-900 bg-white placeholder-slate-400 focus:outline-none focus:border-[#8e3a59] focus:ring-2 focus:ring-[#8e3a59]/20 transition-all"
                  placeholder="Enter password"
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

            {/* Remember me */}
            <div className="flex items-center justify-between py-1">
              <label className="flex items-center gap-2.5 cursor-pointer text-xs text-slate-600 select-none">
                <input
                  type="checkbox"
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                  className="w-4 h-4 rounded text-[#8e3a59] border-slate-300 focus:ring-[#8e3a59]"
                />
                <span>Keep session active</span>
              </label>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading || !email || !password}
              className="w-full h-12 rounded-lg bg-[#8e3a59] hover:bg-[#752d48] disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-semibold shadow-md shadow-[#8e3a59]/30 hover:shadow-lg transition-all flex items-center justify-center gap-2"
            >
              {loading ? (
                <span>Authenticating...</span>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Bottom Links */}
          <div className="mt-10 pt-8 border-t border-slate-200 text-center space-y-4">
            <p className="text-sm text-slate-600">
              New organization?{' '}
              <button
                onClick={() => setCurrentPage('register')}
                className="font-bold text-[#8e3a59] hover:underline ml-1"
              >
                Register Now
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
