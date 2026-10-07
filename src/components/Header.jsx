import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { Cpu, Bell, ChevronDown, ShieldCheck, Activity } from 'lucide-react';

export const Header = () => {
  const {
    currentPage,
    setCurrentPage,
    user,
    activeDisruption,
    logout,
    currentRole,
    setCurrentRole,
    roles,
  } = useApp();
  const [showRoleMenu, setShowRoleMenu] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const activeRoleObj = roles?.find((r) => r.id === currentRole);

  const authPages = ['landing', 'login', 'register', 'forgot_password'];
  if (authPages.includes(currentPage)) return null;

  return (
    <header
      className="sticky top-0 z-40 px-6 py-3 flex items-center justify-between bg-white border-b border-slate-200"
    >
      {/* Brand */}
      <div
        className="flex items-center gap-3 cursor-pointer"
        onClick={() => setCurrentPage('dashboard')}
      >
        <div className="w-8 h-8 rounded-md flex items-center justify-center bg-[#8e3a59] text-white shadow-sm">
          <Cpu className="w-4 h-4" />
        </div>
        <div>
          <p className="font-bold tracking-tight text-sm uppercase text-slate-900">
            RIMBERIO AI
          </p>
          <p className="font-mono text-[10px] text-slate-500">
            Supply Chain Twin
          </p>
        </div>

        {/* Live Badge */}
        <div className="hidden lg:flex items-center gap-1.5 ml-4 px-2.5 py-1 rounded-full text-[11px] font-semibold tracking-tight uppercase bg-slate-100 text-slate-700 border border-slate-200">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
          Autonomous Runtime
        </div>

        {/* Disruption Alert */}
        {activeDisruption && (
          <div className="hidden xl:flex items-center gap-1.5 ml-2 px-2.5 py-1 rounded-full text-[11px] font-semibold tracking-tight uppercase bg-amber-50 text-amber-800 border border-amber-200">
            <Activity className="w-3.5 h-3.5 text-amber-600" />
            <span>Suez Disruption Alert Active</span>
          </div>
        )}
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-3">
        {/* Role Persona Switcher */}
        <div className="relative">
          <button
            onClick={() => setShowRoleMenu(!showRoleMenu)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-[6px] border border-[#dfd2d8] hover:bg-[#f7eef2] transition-colors text-xs font-semibold text-[#1a0f15]"
            title="Switch Active Agent Role"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-[#8e3a59]" />
            <span className="hidden sm:inline uppercase text-[11px] font-semibold">
              ROLE: {activeRoleObj?.name || 'Buyer Agent'}
            </span>
            <ChevronDown className="w-3 h-3 text-[#7d6872]" />
          </button>

          {showRoleMenu && (
            <div
              className="absolute right-0 mt-2 w-72 rounded-[6px] p-2 z-50 shadow-lg"
              style={{
                background: 'var(--color-paper-white)',
                border: '1px solid var(--color-stone)',
              }}
            >
              <div className="px-3 py-2 border-b border-[#dfd2d8]">
                <p className="text-[10px] font-bold uppercase text-[#8e3a59] tracking-wider">
                  MULTI-AGENT ROLE ARCHITECTURE
                </p>
                <p className="text-xs text-[#7d6872] mt-0.5">Switch Persona Perspective</p>
              </div>

              <div className="py-1 space-y-1">
                {roles.map((r) => {
                  const isSelected = r.id === currentRole;
                  return (
                    <button
                      key={r.id}
                      onClick={() => {
                        setCurrentRole(r.id);
                        setShowRoleMenu(false);
                      }}
                      className={`w-full text-left p-2 rounded-[6px] transition-all ${
                        isSelected ? 'bg-[#8e3a59] text-white' : 'hover:bg-[#f7eef2] text-[#1a0f15]'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold uppercase">{r.name}</span>
                        <span
                          className={`text-[9px] font-bold px-1.5 py-0.5 rounded-[4px] ${
                            isSelected ? 'bg-white/20 text-white' : 'bg-[#f7eef2] text-[#8e3a59] border border-[#d2b0bd]'
                          }`}
                        >
                          {r.badge}
                        </span>
                      </div>
                      <p
                        className={`text-[10px] mt-0.5 ${
                          isSelected ? 'text-white/80' : 'text-[#7d6872]'
                        }`}
                      >
                        {r.title}
                      </p>
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Bell Notifications */}
        <button
          className="relative p-2 rounded-[6px] transition-colors border border-[#dfd2d8] hover:bg-[#f7eef2]"
          title="System Notifications"
        >
          <Bell className="w-4 h-4 text-[#1a0f15]" />
          <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-[#8e3a59] border border-white"></span>
        </button>

        {/* User Profile */}
        {user && (
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center gap-2.5 px-3 py-1.5 rounded-[6px] border border-[#dfd2d8] transition-colors hover:bg-[#f7eef2]"
            >
              <img
                src={user.avatar}
                alt={user.name}
                className="w-6 h-6 rounded-[4px] object-cover border border-[#dfd2d8]"
              />
              <div className="hidden md:block text-left">
                <p className="text-xs font-bold leading-tight text-[#1a0f15]">
                  {user.name}
                </p>
                <p className="rim-mono text-[9px] text-[#7d6872]">
                  {user.role}
                </p>
              </div>
              <ChevronDown className="w-3 h-3 text-[#7d6872]" />
            </button>

            {showUserMenu && (
              <div
                className="absolute right-0 mt-2 w-60 rounded-[6px] p-2 z-50 shadow-lg"
                style={{
                  background: 'var(--color-paper-white)',
                  border: '1px solid var(--color-stone)',
                }}
              >
                <div className="px-3 py-2.5 border-b border-[#dfd2d8]">
                  <p className="text-sm font-bold text-[#1a0f15]">
                    {user.name}
                  </p>
                  <p className="rim-mono text-xs text-[#7d6872]">
                    {user.email}
                  </p>
                  <span className="badge badge-brand mt-2">{user.company}</span>
                </div>
                <div className="py-1 space-y-0.5">
                  {[
                    { label: 'Intelligence Dashboard', id: 'dashboard' },
                    { label: 'Negotiation Console', id: 'negotiation' },
                    { label: 'Reports & Audits', id: 'reports' },
                  ].map(({ label, id }) => (
                    <button
                      key={id}
                      onClick={() => {
                        setCurrentPage(id);
                        setShowUserMenu(false);
                      }}
                      className="w-full text-left px-3 py-2 rounded-[6px] text-xs font-semibold uppercase tracking-wider transition-colors hover:bg-[#f7eef2] text-[#1a0f15]"
                      style={{ fontSize: '0.6875rem' }}
                    >
                      {label}
                    </button>
                  ))}
                </div>
                <div className="pt-1 border-t border-[#dfd2d8]">
                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      logout();
                    }}
                    className="w-full text-left px-3 py-2 rounded-[6px] text-xs font-bold uppercase tracking-wider transition-colors hover:bg-red-50 text-red-700"
                    style={{ fontSize: '0.6875rem' }}
                  >
                    Sign Out
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
};
