/**
 * RIMBERIO Enterprise Dynamic Sidebar
 * =====================================
 * Navigation items come from the backend via /me/navigation.
 * Grouped by section. Fully role-aware.
 * NO hardcoded pages. NO static navigation.
 */
import React from 'react';
import { useApp } from '../context/AppContext';
import {
  LayoutDashboard, Users, Building2, Shield, Brain, Globe, FileText, Activity,
  Search, MessageSquare, FileCheck, BarChart3, Sliders, Zap, ShoppingCart,
  TrendingUp, Package, AlertTriangle, Target, PieChart, Truck, MapPin,
  Ship, Clock, ClipboardCheck, AlertCircle, DollarSign, TrendingDown,
  Building, ShoppingBag, Bell, HelpCircle, LogOut,
} from 'lucide-react';

// Map icon string names to Lucide components
const ICON_MAP = {
  LayoutDashboard, Users, Building2, Shield, Brain, Globe, FileText, Activity,
  Search, MessageSquare, FileCheck, BarChart3, Sliders, Zap, ShoppingCart,
  TrendingUp, Package, AlertTriangle, Target, PieChart, Truck, MapPin,
  Ship, Clock, ClipboardCheck, AlertCircle, DollarSign, TrendingDown,
  Building, ShoppingBag, Bell, HelpCircle,
};

export const Sidebar = () => {
  const { currentPage, setCurrentPage, navigation, user, logout } = useApp();

  // Don't render on auth pages
  const authPages = ['landing', 'login', 'register', 'forgot_password'];
  if (authPages.includes(currentPage)) return null;
  if (!user) return null;

  const sections = navigation?.sections || {};
  const sectionEntries = Object.entries(sections);

  return (
    <aside
      className="w-[260px] shrink-0 flex flex-col justify-between bg-white border-r border-slate-200"
      style={{ minHeight: 'calc(100vh - 58px)' }}
    >
      <div className="p-3 space-y-3 overflow-y-auto flex-1">
        {sectionEntries.map(([sectionName, items]) => (
          <div key={sectionName}>
            <p className="px-3 mb-1.5 text-[9px] font-bold uppercase tracking-[0.08em] text-[#8e3a59]/70">
              {sectionName.replace(/_/g, ' ')}
            </p>
            <nav className="space-y-0.5">
              {items.map(({ id, label, icon }) => {
                const isActive = currentPage === id;
                const IconComponent = ICON_MAP[icon] || LayoutDashboard;
                return (
                  <button
                    key={id}
                    onClick={() => setCurrentPage(id)}
                    className={`w-full flex items-center gap-2.5 min-h-[36px] px-3 py-2 rounded-md text-xs font-semibold tracking-tight transition-all ${
                      isActive
                        ? 'bg-[#8e3a59]/10 text-[#8e3a59] font-bold'
                        : 'hover:bg-slate-50 text-slate-700'
                    }`}
                  >
                    <IconComponent
                      className="w-4 h-4 shrink-0"
                      style={{ color: isActive ? '#8e3a59' : '#64748b' }}
                    />
                    <span className="truncate" style={{ fontSize: '0.75rem' }}>
                      {label}
                    </span>
                  </button>
                );
              })}
            </nav>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-slate-200">
        {/* Role Info */}
        <div className="p-3 rounded-lg mb-2 bg-slate-50 border border-slate-200">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[9px] font-bold uppercase tracking-wider text-[#8e3a59]">
              Active Role
            </span>
          </div>
          <p className="text-xs font-semibold text-slate-900">
            {navigation?.role_display || user?.role_display || user?.role || 'User'}
          </p>
          {user?.department?.name && (
            <p className="text-[10px] text-slate-500 mt-0.5">
              {user.department.name}
            </p>
          )}
          {user?.organization?.name && (
            <p className="text-[10px] text-slate-400 mt-0.5">
              {user.organization.name}
            </p>
          )}
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
