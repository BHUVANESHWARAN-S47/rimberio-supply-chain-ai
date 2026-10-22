/**
 * RIMBERIO Enterprise Header
 * ============================
 * Shows: brand, user profile with real data, role display.
 * NO fake role switcher. NO AI agent persona selector.
 */
import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { Cpu, Bell, ChevronDown, Shield, LogOut } from 'lucide-react';

export const Header = () => {
  const { currentPage, setCurrentPage, user, logout, navigation } = useApp();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const authPages = ['landing', 'login', 'register', 'forgot_password'];
  if (authPages.includes(currentPage)) return null;
  if (!user) return null;

  const avatarUrl = user.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.full_name || 'U')}&background=8e3a59&color=fff&bold=true&size=64`;

  return (
    <header className="sticky top-0 z-40 px-6 py-3 flex items-center justify-between bg-white border-b border-slate-200">
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
            RIMBERIO
          </p>
          <p className="font-mono text-[10px] text-slate-500">
            Enterprise Supply Chain
          </p>
        </div>

        {/* Org Badge */}
        {user.organization?.name && (
          <div className="hidden lg:flex items-center gap-1.5 ml-4 px-2.5 py-1 rounded-full text-[11px] font-semibold tracking-tight bg-slate-100 text-slate-700 border border-slate-200">
            {user.organization.name}
          </div>
        )}
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-3">
        {/* INR Currency Badge */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-800" title="System Currency: Indian Rupee (INR)">
          <span className="text-sm font-bold">₹</span>
          <span className="text-[10px] font-mono tracking-wider font-extrabold uppercase">INR</span>
        </div>

        {/* Role Badge */}
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-[#dfd2d8] bg-[#f7eef2]/50 text-xs font-semibold text-[#8e3a59]">
          <Shield className="w-3.5 h-3.5" />
          <span className="uppercase text-[11px]">
            {navigation?.role_display || user.role_display || user.role || 'User'}
          </span>
        </div>

        {/* Notifications */}
        <button
          className="relative p-2 rounded-md transition-colors border border-slate-200 hover:bg-slate-50"
          title="Notifications"
        >
          <Bell className="w-4 h-4 text-slate-600" />
        </button>

        {/* User Profile Menu */}
        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2.5 px-3 py-1.5 rounded-md border border-slate-200 transition-colors hover:bg-slate-50"
          >
            <img
              src={avatarUrl}
              alt={user.full_name}
              className="w-6 h-6 rounded object-cover border border-slate-200"
            />
            <div className="hidden md:block text-left">
              <p className="text-xs font-bold leading-tight text-slate-900">
                {user.full_name}
              </p>
              <p className="text-[9px] text-slate-500 font-mono">
                {user.department?.name || user.role_display || ''}
              </p>
            </div>
            <ChevronDown className="w-3 h-3 text-slate-400" />
          </button>

          {showUserMenu && (
            <>
              {/* Click-away backdrop */}
              <div
                className="fixed inset-0 z-40"
                onClick={() => setShowUserMenu(false)}
              />
              <div className="absolute right-0 mt-2 w-64 rounded-lg p-2 z-50 shadow-lg bg-white border border-slate-200">
                <div className="px-3 py-2.5 border-b border-slate-200">
                  <p className="text-sm font-bold text-slate-900">{user.full_name}</p>
                  <p className="text-xs text-slate-500 font-mono">{user.email}</p>
                  {user.organization?.name && (
                    <span className="inline-block mt-1.5 px-2 py-0.5 rounded text-[9px] font-bold bg-[#8e3a59]/10 text-[#8e3a59]">
                      {user.organization.name}
                    </span>
                  )}
                </div>
                <div className="py-1 space-y-0.5">
                  <button
                    onClick={() => { setCurrentPage('dashboard'); setShowUserMenu(false); }}
                    className="w-full text-left px-3 py-2 rounded-md text-xs font-semibold transition-colors hover:bg-slate-50 text-slate-700"
                  >
                    Dashboard
                  </button>
                </div>
                <div className="pt-1 border-t border-slate-200">
                  <button
                    onClick={() => { setShowUserMenu(false); logout(); }}
                    className="w-full text-left px-3 py-2 rounded-md text-xs font-bold transition-colors hover:bg-red-50 text-red-700 flex items-center gap-2"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    Sign Out
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
};
