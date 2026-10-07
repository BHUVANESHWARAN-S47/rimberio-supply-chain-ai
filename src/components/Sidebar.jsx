import React from 'react';
import { useApp } from '../context/AppContext';
import {
  LayoutDashboard,
  Bot,
  Sliders,
  Users,
  Zap,
  FileText,
  LogOut,
  BellRing,
  Brain,
} from 'lucide-react';

export const Sidebar = () => {
  const { currentPage, setCurrentPage, logout } = useApp();

  const authPages = ['landing', 'login', 'register', 'forgot_password'];
  if (authPages.includes(currentPage)) return null;

  const mainNav = [
    {
      id: 'dashboard',
      label: 'Intelligence Dashboard',
      icon: LayoutDashboard,
      badge: 'LIVE',
      badgeClass: 'badge-healthy',
    },
    {
      id: 'negotiation',
      label: 'AI Negotiation Console',
      icon: Bot,
      badge: 'AI',
      badgeClass: 'badge-brand',
    },
    {
      id: 'simulation',
      label: 'Counterfactual Twin Sim',
      icon: Sliders,
      badge: 'SIM',
      badgeClass: 'badge-bone',
    },
    {
      id: 'suppliers',
      label: 'Supplier Workspace',
      icon: Users,
      badge: '98%',
      badgeClass: 'badge-healthy',
    },
    {
      id: 'decision_center',
      label: 'Adaptive Decision Center',
      icon: Zap,
      badge: 'AUTO',
      badgeClass: 'badge-brand',
    },
    {
      id: 'customer_impact',
      label: 'Customer Impact & Notices',
      icon: BellRing,
      badge: 'CLIENT',
      badgeClass: 'badge-healthy',
    },
    {
      id: 'learning_feedback',
      label: 'Learning Loop & Confusion Mat',
      icon: Brain,
      badge: 'LEARN',
      badgeClass: 'badge-brand',
    },
    { id: 'reports', label: 'Reports & Architecture', icon: FileText },
  ];

  return (
    <aside
      className="w-[280px] shrink-0 flex flex-col justify-between bg-white border-r border-slate-200"
      style={{
        minHeight: 'calc(100vh - 58px)',
      }}
    >
      <div className="p-3 space-y-4">
        {/* Main Navigation */}
        <div>
          <p className="px-3 mb-2 text-[10px] font-bold uppercase tracking-wider text-[#8e3a59]">
            Digital Twin Platform
          </p>
          <nav className="space-y-1">
            {mainNav.map(({ id, label, icon: Icon, badge, badgeClass }) => {
              const isActive = currentPage === id;
              return (
                <button
                  key={id}
                  onClick={() => setCurrentPage(id)}
                  className={`w-full flex items-center justify-between min-h-[38px] px-3 py-2 rounded-md text-xs font-semibold tracking-tight transition-all ${
                    isActive ? 'bg-slate-100 text-[#8e3a59] font-bold' : 'hover:bg-slate-50 text-slate-700'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0 mr-2">
                    <Icon
                      className="w-4 h-4 shrink-0"
                      style={{ color: isActive ? '#8e3a59' : '#64748b' }}
                    />
                    <span
                      className="truncate font-semibold text-slate-900"
                      style={{ fontSize: '0.75rem', letterSpacing: '-0.01em' }}
                    >
                      {label}
                    </span>
                  </div>
                  {badge && (
                    <span
                      className={`badge ${badgeClass} shrink-0`}
                      style={{ fontSize: '9px', padding: '2px 6px', lineHeight: 1 }}
                    >
                      {badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Sidebar Footer */}
      <div className="p-3 border-t border-slate-200">
        {/* Digital Twin Status Widget */}
        <div className="p-3 rounded-lg mb-2 bg-slate-50 border border-slate-200">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#8e3a59]">
              Twin Node Status
            </span>
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          </div>
          <p className="text-xs font-medium text-slate-900">
            142 warehouse telemetry streams active
          </p>
          <div className="flex justify-between mt-2 pt-1 border-t border-slate-200">
            <span className="font-mono text-[10px] text-slate-500">
              14ms ping
            </span>
            <span className="font-mono text-[10px] font-bold text-[#8e3a59]">
              99.98% uptime
            </span>
          </div>
        </div>

        {/* Logout */}
        <button
          onClick={logout}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-md text-xs font-semibold uppercase tracking-wider transition-colors hover:bg-rose-50 text-slate-700 hover:text-rose-700 border border-transparent hover:border-rose-200"
        >
          <LogOut className="w-4 h-4 text-rose-600" />
          <span style={{ fontSize: '0.6875rem', letterSpacing: '0.05em' }}>
            Sign Out
          </span>
        </button>
      </div>
    </aside>
  );
};
