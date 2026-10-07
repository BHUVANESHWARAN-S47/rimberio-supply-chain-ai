import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { Cpu, Mail, ArrowLeft, ShieldAlert, CheckCircle } from 'lucide-react';

export const ForgotPasswordPage = () => {
  const { setCurrentPage } = useApp();
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setSent(true);
  };

  return (
    <div
      className="min-h-screen flex flex-col justify-between"
      style={{ background: 'var(--color-paper-white)' }}
    >
      <header
        className="px-8 py-5 flex items-center justify-between"
        style={{ background: 'var(--color-paper-white)', borderBottom: '1px solid var(--color-stone)' }}
      >
        <div
          className="flex items-center gap-3 cursor-pointer"
          onClick={() => setCurrentPage('landing')}
        >
          <div className="w-9 h-9 rounded-[6px] flex items-center justify-center bg-[#8e3a59]">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <span
            className="font-bold tracking-tight text-sm uppercase text-[#1a0f15]"
            style={{ letterSpacing: '-0.01em' }}
          >
            RIMBERIO
          </span>
        </div>
        <button
          onClick={() => setCurrentPage('login')}
          className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider transition-colors hover:text-[#8e3a59] text-[#1a0f15]"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Sign In
        </button>
      </header>

      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md p-8 rounded-[6px] bg-white border border-[#dfd2d8] shadow-sm">
          <div className="text-center mb-6">
            <div className="w-12 h-12 rounded-[6px] flex items-center justify-center mx-auto mb-4 bg-[#f7eef2] border border-[#d2b0bd]">
              <ShieldAlert className="w-6 h-6 text-[#8e3a59]" />
            </div>
            <p className="rim-section-title mb-1 text-[#8e3a59]">Security Recovery</p>
            <h2 className="text-2xl font-bold text-[#1a0f15]" style={{ letterSpacing: '-0.02em' }}>
              CREDENTIAL RECOVERY
            </h2>
            <p className="text-xs mt-2 text-[#7d6872]">
              Request a zero-trust security key reset for your Rimberio enterprise identity.
            </p>
          </div>

          {sent ? (
            <div
              className="p-5 rounded-[6px] text-center space-y-3 bg-[#edf7f0] border border-[#b6e2c8]"
            >
              <CheckCircle className="w-8 h-8 text-[#176537] mx-auto" />
              <h4 className="font-bold text-sm text-[#176537]">Recovery Instructions Sent</h4>
              <p className="text-xs text-[#2e523b]">
                An encrypted security reset link was dispatched to{' '}
                <span className="font-mono font-bold text-[#1a0f15]">{email}</span>.
              </p>
              <button
                onClick={() => setCurrentPage('login')}
                className="rim-btn-primary w-full mt-2 text-xs"
              >
                Return to Enterprise Login
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold tracking-tight uppercase mb-1.5 text-[#1a0f15]">
                  Enterprise Email
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#8e3a59] pointer-events-none" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="rim-input pl-11 text-xs"
                    placeholder="name@rimberio.ai"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="rim-btn-primary w-full"
                style={{ padding: '12px 20px', fontSize: '13px' }}
              >
                Dispatch Encrypted Reset Link
              </button>
            </form>
          )}

          <div className="mt-6 pt-5 border-t border-[#dfd2d8] text-center">
            <button
              onClick={() => setCurrentPage('login')}
              className="text-xs text-[#7d6872] hover:text-[#8e3a59] transition-colors"
            >
              Remember password? Sign in
            </button>
          </div>
        </div>
      </div>

      <footer className="px-8 py-4 border-t border-[#dfd2d8] text-center text-xs text-[#7d6872] bg-white">
        © 2026 RIMBERIO AI · Zero Trust Enterprise Access
      </footer>
    </div>
  );
};
