import React, { useEffect, useState } from 'react';
import {
  Bot,
  CheckCircle2,
  Send,
  Pause,
  Play,
  Sparkles,
  RefreshCw,
  Plus,
  ArrowRight,
  ChevronDown,
  ChevronUp,
  X,
  Building2,
  Package,
  ShieldCheck,
  XCircle,
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { RimberioAPI } from '../services/api';
import { formatINR } from '../utils/currency';
import {
  HelpTooltip,
  StatusBadge,
  DeleteConfirmDialog,
  EmptyState,
  Toast,
} from '../components/common/CommonUI';

export const NegotiationPage = () => {
  const { user, setCurrentPage } = useApp();
  const isSupplier = user?.role === 'SUPPLIER';

  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');
  const [showDetails, setShowDetails] = useState(false);

  // Start Modal
  const [showStartModal, setShowStartModal] = useState(false);
  const [products, setProducts] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [startForm, setStartForm] = useState({
    sku_code: 'SKU-MC-772',
    supplier_code: 'SUP-001',
    target_price: 140,
  });

  // Manual Takeover / Counter Offer Modal
  const [showManualModal, setShowManualModal] = useState(false);
  const [manualPrice, setManualPrice] = useState(145);
  const [manualDays, setManualDays] = useState(10);

  const loadSession = async (sessionId = 'SES-AUTONOMOUS-01') => {
    setLoading(true);
    try {
      const data = await RimberioAPI.getNegotiationSession(sessionId);
      setSession(data);
    } catch (err) {
      console.warn('Could not load negotiation session:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSession();
    Promise.all([
      RimberioAPI.getProducts().catch(() => []),
      RimberioAPI.getSuppliers().catch(() => []),
    ]).then(([prodRes, suppRes]) => {
      setProducts(Array.isArray(prodRes) ? prodRes : []);
      setSuppliers(Array.isArray(suppRes) ? suppRes : []);
    });
  }, []);

  const handleStartNegotiation = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const selectedSupplier = suppliers.find((s) => s.code === startForm.supplier_code);
      const res = await RimberioAPI.startNegotiation({
        supplier_code: startForm.supplier_code,
        supplier_name: selectedSupplier?.name || 'Selected Supplier',
        sku_code: startForm.sku_code,
        target_price: parseFloat(startForm.target_price),
      });
      setSession(res);
      setToastMessage('New Price Talk session initiated.');
      setToastType('success');
      setShowStartModal(false);
    } catch (err) {
      setToastMessage(err.message || 'Failed to start negotiation');
      setToastType('error');
    } finally {
      setLoading(false);
    }
  };

  const handleNextRound = async (customOffer = null) => {
    if (!session) return;
    setLoading(true);
    try {
      const payload = {
        session_id: session.session_id,
        force_concession: true,
        custom_buyer_offer: customOffer !== null ? customOffer : session.buyer_target,
      };
      const updated = await RimberioAPI.stepNegotiation(payload);
      setSession(updated);
      setToastMessage(`Round ${updated.current_round} completed.`);
      setToastType('success');
    } catch (err) {
      setToastMessage(err.message || 'Next round failed');
      setToastType('error');
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptDeal = async () => {
    if (!session) return;
    setLoading(true);
    try {
      // Create confirmed purchase order from accepted deal
      const poNum = `PO-${Math.floor(10000 + Math.random() * 90000)}`;
      await RimberioAPI.createPurchaseOrder({
        po_number: poNum,
        supplier_id: session.supplier_code,
        total_amount: Number(session.current_offer) * 1000,
        status: 'APPROVED',
      });

      setSession({
        ...session,
        status: 'AGREED',
      });
      setToastMessage(`Deal accepted! Purchase Order ${poNum} generated.`);
      setToastType('success');
    } catch (err) {
      setToastMessage(err.message || 'Failed to finalize deal');
      setToastType('error');
    } finally {
      setLoading(false);
    }
  };

  const handleRejectDeal = () => {
    if (!session) return;
    setSession({
      ...session,
      status: 'REJECTED',
    });
    setToastMessage('Price Talk session closed without agreement.');
    setToastType('info');
  };

  const handleManualSubmit = async (e) => {
    e.preventDefault();
    setShowManualModal(false);
    await handleNextRound(parseFloat(manualPrice));
  };

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-xl bg-white border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider bg-[#8e3a59]/10 text-[#8e3a59]">
              <Bot className="w-3.5 h-3.5" />
              {isSupplier ? 'Supplier Price Talks' : 'Let AI Negotiate Price'}
            </span>
            <span className="text-xs font-mono text-slate-500">
              Session: {session?.session_id || 'SES-AUTONOMOUS-01'}
            </span>
          </div>
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              Price Talks
            </h1>
            <HelpTooltip text="Autonomous negotiation timeline between buyer and supplier agents to agree on competitive prices and delivery days." />
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Product: <strong className="text-slate-700">{session?.sku_code || 'Micro-Capacitor'}</strong> · Supplier: <strong className="text-slate-700">{session?.supplier_name || 'Apex Global Electronics'}</strong>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => loadSession(session?.session_id)}
            disabled={loading}
            className="px-3.5 py-2 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 transition-colors flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          {!isSupplier && (
            <button
              onClick={() => setShowStartModal(true)}
              className="px-4 py-2 rounded-lg bg-[#8e3a59] hover:bg-[#782f49] text-white text-xs font-bold shadow-sm transition-colors flex items-center gap-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              Start AI Negotiation
            </button>
          )}
        </div>
      </div>

      {/* 4 Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Current Supplier Offer</span>
          <div className="text-2xl font-bold text-slate-900 mt-1 font-mono">
            {session?.current_offer ? formatINR(session.current_offer, 2) : '₹0.00'}
          </div>
          <p className="text-[11px] text-slate-400 mt-0.5">Per unit spot price</p>
        </div>

        {/* Hide Buyer Target from Supplier! */}
        {!isSupplier ? (
          <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
            <span className="text-xs text-slate-500 font-medium">My Target Price</span>
            <div className="text-2xl font-bold text-[#8e3a59] mt-1 font-mono">
              {session?.buyer_target ? formatINR(session.buyer_target, 2) : '₹0.00'}
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">Autonomous goal</p>
          </div>
        ) : (
          <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
            <span className="text-xs text-slate-500 font-medium">Negotiation Status</span>
            <div className="text-xl font-bold text-slate-900 mt-1">
              <StatusBadge status={session?.status || 'ACTIVE'} />
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">Commercial agreement state</p>
          </div>
        )}

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Delivery Days</span>
          <div className="text-2xl font-bold text-slate-900 mt-1">
            {session?.agreed_lead_time || '12 Days'}
          </div>
          <p className="text-[11px] text-slate-400 mt-0.5">Agreed transit schedule</p>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">AI Confidence</span>
          <div className="text-2xl font-bold text-emerald-700 mt-1">
            {session?.agent_confidence && session.agent_confidence > 80 ? 'High' : 'Moderate'}
          </div>
          <p className="text-[11px] text-slate-400 mt-0.5">Fair market equilibrium</p>
        </div>
      </div>

      {/* Main Action Bar */}
      <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-700">Talk Status:</span>
          <StatusBadge status={session?.status || 'ACTIVE'} />
          <span className="text-xs text-slate-400 ml-2">Round {session?.current_round || 1} of {session?.max_rounds || 10}</span>
        </div>

        {session?.status === 'ACTIVE' && (
          <div className="flex items-center flex-wrap gap-2">
            {!isSupplier ? (
              <>
                <button
                  onClick={() => handleNextRound()}
                  disabled={loading}
                  className="px-4 py-2 rounded-lg bg-[#8e3a59] hover:bg-[#782f49] text-white text-xs font-bold shadow-sm transition-colors flex items-center gap-1.5"
                >
                  <ArrowRight className="w-3.5 h-3.5" />
                  Next Round
                </button>
                <button
                  onClick={handleAcceptDeal}
                  disabled={loading}
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-sm transition-colors flex items-center gap-1.5"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Accept Deal
                </button>
                <button
                  onClick={() => setShowManualModal(true)}
                  disabled={loading}
                  className="px-3.5 py-2 rounded-lg border border-slate-300 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
                >
                  Take Over Manually
                </button>
                <button
                  onClick={handleRejectDeal}
                  disabled={loading}
                  className="px-3.5 py-2 rounded-lg border border-rose-200 text-xs font-semibold text-rose-700 hover:bg-rose-50 transition-colors"
                >
                  Reject
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={handleAcceptDeal}
                  disabled={loading}
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-sm"
                >
                  Accept Offer
                </button>
                <button
                  onClick={() => setShowManualModal(true)}
                  disabled={loading}
                  className="px-4 py-2 rounded-lg bg-[#8e3a59] hover:bg-[#782f49] text-white text-xs font-bold shadow-sm"
                >
                  Counter Offer
                </button>
                <button
                  onClick={handleRejectDeal}
                  disabled={loading}
                  className="px-3.5 py-2 rounded-lg border border-rose-200 text-xs font-semibold text-rose-700 hover:bg-rose-50"
                >
                  Decline
                </button>
              </>
            )}
          </div>
        )}
      </div>

      {/* Round-by-Round Timeline */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <h3 className="text-base font-bold text-slate-900">Round-by-Round Timeline</h3>
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="text-xs font-semibold text-[#8e3a59] hover:underline flex items-center gap-1"
          >
            {showDetails ? 'Hide details' : 'Show details'}
            {showDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Details card if toggled */}
        {showDetails && (
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-2">
            <p className="font-bold text-slate-800">Autonomous Agent Algorithm Architecture</p>
            <p className="text-slate-600 leading-relaxed">
              Consensus negotiation utilizes Faratin bilateral concession heuristics along a directed acyclic graph (DAG). The state machine autonomously calculates Pareto-optimal concessions balancing landed cost against supplier lead-time elasticity.
            </p>
          </div>
        )}

        <div className="space-y-4">
          {(session?.history || []).map((bid, idx) => {
            const isBuyer = bid.role === 'BUYER';
            const isLogistics = bid.role === 'LOGISTICS';

            return (
              <div
                key={idx}
                className={`p-4 rounded-xl border transition-all ${
                  isBuyer
                    ? 'bg-[#8e3a59]/5 border-[#8e3a59]/20 ml-0 mr-8'
                    : isLogistics
                    ? 'bg-blue-50/50 border-blue-200 mx-4'
                    : 'bg-slate-50 border-slate-200 ml-8 mr-0'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-xs text-slate-900">
                      Round {bid.round}: {isBuyer ? 'My Offer (Buyer)' : isLogistics ? 'Logistics Assessment' : 'Supplier Offer'}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {bid.agent_name || bid.agent_id}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-mono font-bold text-xs text-slate-900">
                      {formatINR(bid.proposed_price, 2)} / unit
                    </span>
                    <span className="text-[11px] text-slate-500 font-medium">
                      {bid.proposed_lead_time_days} days
                    </span>
                  </div>
                </div>

                <p className="text-xs text-slate-700 leading-relaxed">{bid.message}</p>
              </div>
            );
          })}

          {(!session?.history || session.history.length === 0) && (
            <p className="text-xs text-slate-500 text-center py-6">
              No negotiation rounds recorded. Click "Start AI Negotiation" to begin.
            </p>
          )}
        </div>
      </div>

      {/* Start Negotiation Modal */}
      {showStartModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="w-full max-w-lg bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">Start Price Talk with AI</h3>
              <button
                onClick={() => setShowStartModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleStartNegotiation} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Pick Product</label>
                <select
                  value={startForm.sku_code}
                  onChange={(e) => setStartForm({ ...startForm, sku_code: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                >
                  {products.map((p) => (
                    <option key={p.id || p.sku} value={p.sku}>
                      {p.name} ({p.sku})
                    </option>
                  ))}
                  {products.length === 0 && (
                    <option value="SKU-MC-772">Micro-Capacitor Ceramic Array (SKU-MC-772)</option>
                  )}
                </select>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Pick Supplier</label>
                <select
                  value={startForm.supplier_code}
                  onChange={(e) => setStartForm({ ...startForm, supplier_code: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                >
                  {suppliers.map((s) => (
                    <option key={s.id || s.code} value={s.code || s.id}>
                      {s.name} ({s.code})
                    </option>
                  ))}
                  {suppliers.length === 0 && (
                    <option value="SUP-001">Apex Precision Systems (SUP-001)</option>
                  )}
                </select>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Target Price (₹ / unit)</label>
                <input
                  type="number"
                  step="0.01"
                  value={startForm.target_price}
                  onChange={(e) => setStartForm({ ...startForm, target_price: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowStartModal(false)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-100 border border-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-[#8e3a59] hover:bg-[#782f49] shadow-sm"
                >
                  Start Negotiation
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Manual Takeover / Counter Offer Modal */}
      {showManualModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="w-full max-w-md bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">
                {isSupplier ? 'Submit Counter Offer' : 'Take Over Manually'}
              </h3>
              <button
                onClick={() => setShowManualModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleManualSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Proposed Offer Price (₹)</label>
                <input
                  type="number"
                  step="0.01"
                  value={manualPrice}
                  onChange={(e) => setManualPrice(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Proposed Delivery Days</label>
                <input
                  type="number"
                  value={manualDays}
                  onChange={(e) => setManualDays(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowManualModal(false)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-100 border border-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-[#8e3a59] hover:bg-[#782f49] shadow-sm"
                >
                  Submit Offer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Toast */}
      <Toast
        message={toastMessage}
        type={toastType}
        onClose={() => setToastMessage('')}
      />
    </div>
  );
};
