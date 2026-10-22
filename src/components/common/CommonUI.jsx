import React, { useState, useRef } from 'react';
import { HelpCircle, AlertTriangle, CheckCircle, Info, X, Trash2, Sparkles, ChevronDown, ChevronUp, Send, Loader, MessageSquare } from 'lucide-react';

/**
 * Reusable '?' Help Tooltip next to page titles explaining the page in 1 simple sentence.
 */
export const HelpTooltip = ({ text }) => {
  const [show, setShow] = useState(false);
  return (
    <div className="relative inline-flex items-center ml-2">
      <button
        type="button"
        onClick={() => setShow(!show)}
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
        className="w-5 h-5 rounded-full flex items-center justify-center bg-slate-100 hover:bg-[#8e3a59]/10 text-slate-500 hover:text-[#8e3a59] transition-colors"
        title="Page Help"
      >
        <HelpCircle className="w-3.5 h-3.5" />
      </button>
      {show && (
        <div className="absolute left-7 top-1/2 -translate-y-1/2 z-50 w-72 p-3 bg-slate-900 text-white text-xs rounded-lg shadow-xl pointer-events-none">
          <p className="leading-relaxed font-normal">{text}</p>
        </div>
      )}
    </div>
  );
};

/**
 * Standard Status Badge with plain language words and harmonious colors.
 * Pending, In Progress, Approved, Shipped, Delivered, Delayed, Cancelled.
 */
export const StatusBadge = ({ status }) => {
  const s = (status || 'PENDING').toUpperCase();

  let styles = 'bg-slate-100 text-slate-700 border-slate-200';
  let label = 'Pending';

  if (s.includes('APPROV') || s.includes('ACCEPT') || s.includes('HEALTH') || s.includes('ACTIVE') || s.includes('DELIVERED') || s.includes('RESOLVED')) {
    styles = 'bg-emerald-50 text-emerald-800 border-emerald-200';
    label = s.includes('DELIVERED') ? 'Delivered' : (s.includes('RESOLVED') ? 'Resolved' : 'Approved');
  } else if (s.includes('PROGRESS') || s.includes('TRANSIT') || s.includes('FULFILL')) {
    styles = 'bg-blue-50 text-blue-800 border-blue-200';
    label = s.includes('TRANSIT') ? 'Shipped' : 'In Progress';
  } else if (s.includes('DELAY') || s.includes('WARN') || s.includes('ALERT')) {
    styles = 'bg-amber-50 text-amber-800 border-amber-200';
    label = 'Delayed';
  } else if (s.includes('CANCEL') || s.includes('REJECT') || s.includes('CRITICAL') || s.includes('FAIL') || s.includes('DISABLED')) {
    styles = 'bg-rose-50 text-rose-800 border-rose-200';
    label = s.includes('CANCEL') ? 'Cancelled' : (s.includes('DISABLED') ? 'Disabled' : 'Rejected');
  } else {
    styles = 'bg-slate-100 text-slate-800 border-slate-200';
    label = status || 'Pending';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${styles}`}>
      {label}
    </span>
  );
};

/**
 * Delete Confirmation Dialog
 * Always asks: "Are you sure you want to delete [name]? This cannot be undone." with Cancel / Yes, Delete.
 */
export const DeleteConfirmDialog = ({ isOpen, itemName, onConfirm, onCancel, loading = false }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
      <div className="w-full max-w-md bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-4">
        <div className="flex items-center gap-3 text-rose-600">
          <div className="w-10 h-10 rounded-full bg-rose-50 flex items-center justify-center shrink-0">
            <Trash2 className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">Confirm Deletion</h3>
            <p className="text-xs text-slate-500">This action is permanent</p>
          </div>
        </div>

        <p className="text-sm text-slate-700 leading-relaxed">
          Are you sure you want to delete <strong className="text-slate-900">{itemName || 'this item'}</strong>? This cannot be undone.
        </p>

        <div className="flex items-center justify-end gap-3 pt-2">
          <button
            type="button"
            disabled={loading}
            onClick={onCancel}
            className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-100 border border-slate-300 transition-colors"
          >
            Cancel
          </button>
          <button
            type="button"
            disabled={loading}
            onClick={onConfirm}
            className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 transition-colors shadow-sm disabled:opacity-50"
          >
            {loading ? 'Deleting...' : 'Yes, Delete'}
          </button>
        </div>
      </div>
    </div>
  );
};

/**
 * Friendly Empty State with prompt + primary action button
 */
export const EmptyState = ({ message, actionLabel, onAction }) => (
  <div className="text-center py-12 px-4 rounded-xl border-2 border-dashed border-slate-200 bg-slate-50/50">
    <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-3 text-slate-400">
      <Info className="w-6 h-6" />
    </div>
    <p className="text-sm font-semibold text-slate-700 mb-4">{message || 'No records found.'}</p>
    {actionLabel && onAction && (
      <button
        onClick={onAction}
        className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-bold text-white bg-[#8e3a59] hover:bg-[#782f49] shadow-sm transition-colors"
      >
        {actionLabel}
      </button>
    )}
  </div>
);

/**
 * Toast Notification banner
 */
export const Toast = ({ message, type = 'success', onClose }) => {
  if (!message) return null;
  const isErr = type === 'error';

  return (
    <div className={`fixed bottom-6 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-xl shadow-xl border transition-all ${
      isErr ? 'bg-rose-900 text-white border-rose-800' : 'bg-slate-900 text-white border-slate-800'
    }`}>
      {isErr ? <AlertTriangle className="w-4 h-4 text-rose-300 shrink-0" /> : <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />}
      <span className="text-xs font-medium">{message}</span>
      <button onClick={onClose} className="ml-2 text-slate-400 hover:text-white">
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};

/**
 * AI Assistant Card (Small card on each dashboard, not shown to Customer)
 * Shows 1-3 plain suggestions + interactive Q&A box connected to /api/agents/explain.
 * Agent names, timings, algorithms only appear under "Show details".
 */
export const AIAssistantCard = ({ role = 'BUYER', onActionNotice }) => {
  const [showDetails, setShowDetails] = useState(false);
  const [dismissed, setDismissed] = useState([]);
  const [showChat, setShowChat] = useState(false);

  // Q&A state
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [asking, setAsking] = useState(false);
  const inputRef = useRef(null);

  // Suggestions customized per role in plain language
  const suggestionsMap = {
    ADMIN: [
      { id: 1, text: "Bharat Semiconductor delivery rate improved to 96%. Recommended for priority contracts.", action: "Keep Supplier", details: "Decision Agent Pareto Frontier verified; Confidence: High (96.4%)" },
      { id: 2, text: "System learning model is 92% accurate. Update AI Learning recommended before month end.", action: "Update AI Learning", details: "Recalibration Agent drift: 3.6%; Training set: 5,200 transactions" },
    ],
    BUYER: [
      { id: 1, text: "Offer ₹138/unit to Bharat Semiconductor to lock in a 4.2% discount on Micro-Capacitors.", action: "Accept Tip", details: "Buyer Agent calculated linear utility: Target ₹135, Reservation ₹142.5" },
      { id: 2, text: "Apex Precision has 2 days faster delivery for power components at identical quality.", action: "Compare Now", details: "Price Benchmark Agent: Historical benchmark Z-score: -0.42" },
    ],
    LOGISTICS_MANAGER: [
      { id: 1, text: "Chennai port queue has increased by 1 day. Recommend routing incoming cargo via rail.", action: "Review Route", details: "Logistics AIS Telemetry Agent: Berth congestion index at 78%" },
      { id: 2, text: "Blue Dart road carrier is 97.4% on-time this week. Optimal choice for high-priority shipments.", action: "Set Priority", details: "Carrier Reliability Model: 42 on-time arrivals out of 43 lots" },
    ],
    SUPPLIER: [
      { id: 1, text: "Offer 4% discount for orders over 2,500 units to win more buyer purchase commitments.", action: "Apply Discount", details: "Supplier Faratin Model: Concession margin preservation active" },
    ],
    SUPPLY_CHAIN_ANALYST: [
      { id: 1, text: "Demand forecast shows a 12% spike next month. Suggest increasing stock buffer by 800 units.", action: "Plan Stock", details: "Adaptive Decision Agent: demand probability score 0.81" },
    ],
  };

  const currentList = (suggestionsMap[role.toUpperCase()] || suggestionsMap.BUYER).filter(s => !dismissed.includes(s.id));

  const API_BASE = typeof window !== 'undefined'
    ? (window.__RIMBERIO_API_BASE__ || 'http://127.0.0.1:8000')
    : 'http://127.0.0.1:8000';

  const handleAskAI = async (e) => {
    e?.preventDefault();
    const q = question.trim();
    if (!q || asking) return;

    const userMsg = { role: 'user', text: q, ts: new Date().toLocaleTimeString() };
    setChatHistory(prev => [...prev, userMsg]);
    setQuestion('');
    setAsking(true);

    try {
      const token = localStorage.getItem('rimberio_token');
      const res = await fetch(`${API_BASE}/api/agents/explain`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          mode: 'INTERACTIVE_CHAT',
          user_query: q,
          decision_context: { role: role.toUpperCase(), source: 'dashboard_ai_assistant' },
        }),
      });

      let answerText = '';
      if (res.ok) {
        const data = await res.json();
        // ExplanationResponse shape: summary, full_narrative, causal_reasoning_points, actionable_recommendations
        const parts = [];
        if (data?.summary) parts.push(data.summary);
        if (data?.full_narrative && data.full_narrative !== data.summary) parts.push(data.full_narrative);
        if (Array.isArray(data?.actionable_recommendations) && data.actionable_recommendations.length > 0) {
          parts.push('Recommendations: ' + data.actionable_recommendations.slice(0, 3).join('; '));
        }
        answerText = parts.join('\n\n') ||
          data?.explanation || data?.answer || data?.message ||
          'The AI agent processed your question. Please check the suggestion cards above.';
      } else {
        answerText = 'I could not reach the AI engine right now. Please check that the backend server is running and try again.';
      }

      setChatHistory(prev => [
        ...prev,
        { role: 'ai', text: answerText, ts: new Date().toLocaleTimeString() },
      ]);
    } catch {
      setChatHistory(prev => [
        ...prev,
        {
          role: 'ai',
          text: 'Backend is not reachable. Start the server with `python -m uvicorn backend.main:app` and refresh.',
          ts: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setAsking(false);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAskAI();
    }
  };

  if (currentList.length === 0 && !showChat) return null;

  return (
    <div className="rounded-xl bg-gradient-to-r from-slate-900 to-slate-800 text-white shadow-sm border border-slate-700 overflow-hidden">
      {/* ── Header ── */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-[#8e3a59] flex items-center justify-center text-white">
            <Sparkles className="w-3.5 h-3.5" />
          </div>
          <span className="text-xs font-bold tracking-tight uppercase">AI Assistant</span>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-medium">Active</span>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="text-[11px] text-slate-300 hover:text-white flex items-center gap-1 font-medium transition-colors"
          >
            {showDetails ? 'Hide details' : 'Show details'}
            {showDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
          <button
            onClick={() => setShowChat(!showChat)}
            className={`text-[11px] flex items-center gap-1 font-medium px-2.5 py-1 rounded-md transition-colors ${showChat ? 'bg-[#8e3a59] text-white' : 'text-slate-300 hover:text-white hover:bg-white/10'}`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            Ask AI
          </button>
        </div>
      </div>

      {/* ── Suggestion chips ── */}
      {currentList.length > 0 && (
        <div className="p-4 space-y-2.5">
          {currentList.map(item => (
            <div key={item.id} className="p-3 rounded-lg bg-white/5 border border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
              <div className="flex-1">
                <p className="text-xs font-medium text-slate-200">{item.text}</p>
                {showDetails && (
                  <p className="text-[10px] text-slate-400 mt-1 font-mono">{item.details}</p>
                )}
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={() => {
                    onActionNotice?.(`Applied: ${item.action}`);
                    setDismissed([...dismissed, item.id]);
                  }}
                  className="px-2.5 py-1 rounded-md text-[11px] font-bold bg-[#8e3a59] hover:bg-[#a64569] text-white transition-colors"
                >
                  Accept
                </button>
                <button
                  onClick={() => setDismissed([...dismissed, item.id])}
                  className="px-2 py-1 rounded-md text-[11px] font-medium text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                >
                  Ignore
                </button>
                <button
                  onClick={() => {
                    setShowChat(true);
                    setQuestion(`Explain: "${item.text.slice(0, 80)}"`);
                    setTimeout(() => inputRef.current?.focus(), 80);
                  }}
                  className="px-2 py-1 rounded-md text-[11px] font-medium text-slate-300 hover:text-white hover:bg-white/10 transition-colors"
                >
                  Ask AI to explain
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── Interactive Q&A Panel ── */}
      {showChat && (
        <div className="border-t border-white/10 p-4 space-y-3">
          <p className="text-[10px] text-slate-400 font-medium uppercase tracking-wide">Chat with AI Agent</p>

          {/* Message thread */}
          {chatHistory.length > 0 && (
            <div className="max-h-56 overflow-y-auto space-y-2 pr-1 scrollbar-thin scrollbar-thumb-white/10">
              {chatHistory.map((msg, i) => (
                <div
                  key={i}
                  className={`flex flex-col gap-0.5 ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                >
                  <div
                    className={`max-w-[85%] px-3 py-2 rounded-lg text-xs leading-relaxed ${
                      msg.role === 'user'
                        ? 'bg-[#8e3a59]/80 text-white rounded-br-sm'
                        : 'bg-white/10 text-slate-200 rounded-bl-sm'
                    }`}
                  >
                    {msg.text}
                  </div>
                  <span className="text-[9px] text-slate-500 px-1">{msg.ts}</span>
                </div>
              ))}
              {asking && (
                <div className="flex items-start gap-2">
                  <div className="bg-white/10 px-3 py-2 rounded-lg rounded-bl-sm flex items-center gap-2">
                    <Loader className="w-3 h-3 text-slate-400 animate-spin" />
                    <span className="text-[11px] text-slate-400">AI is thinking…</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Input row */}
          <form onSubmit={handleAskAI} className="flex items-center gap-2">
            <input
              ref={inputRef}
              type="text"
              value={question}
              onChange={e => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask any supply chain question…"
              disabled={asking}
              className="flex-1 bg-white/10 border border-white/15 rounded-lg px-3 py-2 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-[#8e3a59] focus:border-[#8e3a59] disabled:opacity-60"
            />
            <button
              type="submit"
              disabled={!question.trim() || asking}
              className="p-2 rounded-lg bg-[#8e3a59] hover:bg-[#a64569] text-white transition-colors disabled:opacity-50 shrink-0"
            >
              {asking ? <Loader className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </button>
          </form>
          <p className="text-[9px] text-slate-500">Powered by RIMBERIO AI Agent Engine · Answers are AI-generated</p>
        </div>
      )}
    </div>
  );
};
