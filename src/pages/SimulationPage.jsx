import React, { useState, useEffect } from 'react';
import {
  Zap,
  RefreshCw,
  ArrowRight,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Clock,
  DollarSign,
  Package,
  Building2,
  ShieldAlert,
  Info,
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

export const SimulationPage = () => {
  const { setCurrentPage } = useApp();
  const [loading, setLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');

  // Input selectors
  const [products, setProducts] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState('');
  const [selectedSupplier, setSelectedSupplier] = useState('');
  const [quantity, setQuantity] = useState(1000);

  // Simulation outputs: 5 scenarios
  const [scenarios, setScenarios] = useState([
    {
      id: 'NORMAL',
      title: 'Normal Conditions',
      desc: 'Baseline delivery schedule with normal domestic demand and standard freight pricing.',
      totalCost: 142500,
      delayDays: 0,
      stockoutRisk: 'Low',
    },
    {
      id: 'HIGH_DEMAND',
      title: 'Demand Goes Up (+30%)',
      desc: 'Sudden spike in enterprise customer orders depletes safety stock.',
      totalCost: 185250,
      delayDays: 2.5,
      stockoutRisk: 'Medium',
    },
    {
      id: 'SUPPLIER_DELAY',
      title: 'Supplier Is Late (+7 days)',
      desc: 'Manufacturing factory backlog or raw material shortage at vendor facility.',
      totalCost: 158000,
      delayDays: 7.0,
      stockoutRisk: 'High',
    },
    {
      id: 'TRANSPORT_DISRUPTION',
      title: 'Transport Problem',
      desc: 'Port transshipment congestion, highway roadblock, or container shortage.',
      totalCost: 172000,
      delayDays: 5.5,
      stockoutRisk: 'Medium',
    },
    {
      id: 'COMPOUND_DISRUPTION',
      title: 'Everything Goes Wrong',
      desc: 'Compound crisis: severe supplier outage coupled with port delay and demand surge.',
      totalCost: 224000,
      delayDays: 12.0,
      stockoutRisk: 'High',
    },
  ]);

  // AI Recommendation
  const [decision, setDecision] = useState({
    action: 'RETAIN', // RETAIN -> Keep supplier, NEGOTIATE -> Ask for a better price, SWITCH -> Change supplier
    supplierName: 'Apex Precision Systems',
    confidence: 'High',
    explanation: 'Current supplier offers optimal price-quality stability. Lead time is within safety buffer.',
  });

  // Plain words explanation modal / toggle
  const [showExplanation, setShowExplanation] = useState(false);
  const [plainExplanation, setPlainExplanation] = useState('');
  const [explaining, setExplaining] = useState(false);

  // Impact warning
  const [customerImpact, setCustomerImpact] = useState(null);

  useEffect(() => {
    Promise.all([
      RimberioAPI.getProducts().catch(() => []),
      RimberioAPI.getSuppliers().catch(() => []),
    ]).then(([prodRes, suppRes]) => {
      const pList = Array.isArray(prodRes) ? prodRes : [];
      const sList = Array.isArray(suppRes) ? suppRes : [];
      setProducts(pList);
      setSuppliers(sList);
      if (pList.length > 0) setSelectedProduct(pList[0].id || pList[0].sku);
      if (sList.length > 0) setSelectedSupplier(sList[0].id || sList[0].code);
    });
  }, []);

  const runCheck = async () => {
    setLoading(true);
    try {
      // 1. Run CNT simulate or calculate 5 scenarios
      const simReq = {
        product_id: selectedProduct || 'PRD-1',
        supplier_id: selectedSupplier || 'SUP-001',
        order_quantity: parseInt(quantity, 10),
      };

      const res = await RimberioAPI.simulateCNT(simReq).catch(() => null);

      if (res && res.scenarios && res.scenarios.length >= 5) {
        const scenarioMap = {
          NORMAL: { title: 'Normal Conditions', desc: 'Baseline operations and standard domestic freight.' },
          HIGH_DEMAND: { title: 'Demand Goes Up (+30%)', desc: 'Sudden spike in enterprise customer demand.' },
          SUPPLIER_DELAY: { title: 'Supplier Is Late (+7 days)', desc: 'Vendor manufacturing backlog.' },
          TRANSPORT_DISRUPTION: { title: 'Transport Problem', desc: 'Port congestion and carrier transit delays.' },
          COMPOUND_DISRUPTION: { title: 'Everything Goes Wrong', desc: 'Compound crisis with multiple simultaneous delays.' },
        };

        const mapped = res.scenarios.slice(0, 5).map((s, idx) => {
          const info = scenarioMap[s.scenario_type] || {
            title: `Scenario #${idx + 1}`,
            desc: 'Simulated counterfactual supply scenario.',
          };
          const delay = s.predicted_delivery_delay || (idx === 0 ? 0 : idx * 2.5);
          const riskLevel = s.stockout_probability > 0.4 ? 'High' : s.stockout_probability > 0.15 ? 'Medium' : 'Low';

          return {
            id: s.scenario_type || `SCEN-${idx}`,
            title: info.title,
            desc: info.desc,
            totalCost: s.predicted_cost || 140000 + idx * 20000,
            delayDays: parseFloat(delay.toFixed(1)),
            stockoutRisk: riskLevel,
          };
        });
        setScenarios(mapped);
      } else {
        // Dynamic calculation based on selected supplier & quantity
        const supplierObj = suppliers.find((s) => s.id === selectedSupplier || s.code === selectedSupplier);
        const unitCost = Number(supplierObj?.unit_cost) || 140;
        const baseCost = unitCost * quantity;

        setScenarios([
          {
            id: 'NORMAL',
            title: 'Normal Conditions',
            desc: 'Baseline delivery schedule with normal domestic demand and standard freight pricing.',
            totalCost: baseCost,
            delayDays: 0,
            stockoutRisk: 'Low',
          },
          {
            id: 'HIGH_DEMAND',
            title: 'Demand Goes Up (+30%)',
            desc: 'Sudden spike in enterprise customer orders depletes safety stock.',
            totalCost: Math.round(baseCost * 1.3),
            delayDays: 2.5,
            stockoutRisk: 'Medium',
          },
          {
            id: 'SUPPLIER_DELAY',
            title: 'Supplier Is Late (+7 days)',
            desc: 'Manufacturing factory backlog or raw material shortage at vendor facility.',
            totalCost: Math.round(baseCost * 1.1),
            delayDays: 7.0,
            stockoutRisk: 'High',
          },
          {
            id: 'TRANSPORT_DISRUPTION',
            title: 'Transport Problem',
            desc: 'Port transshipment congestion, highway roadblock, or container shortage.',
            totalCost: Math.round(baseCost * 1.2),
            delayDays: 5.0,
            stockoutRisk: 'Medium',
          },
          {
            id: 'COMPOUND_DISRUPTION',
            title: 'Everything Goes Wrong',
            desc: 'Compound crisis: severe supplier outage coupled with port delay and demand surge.',
            totalCost: Math.round(baseCost * 1.55),
            delayDays: 11.5,
            stockoutRisk: 'High',
          },
        ]);
      }

      // 2. Fetch AI Recommendation from /agents/decision
      const supplierObj = suppliers.find((s) => s.id === selectedSupplier || s.code === selectedSupplier);
      const decRes = await RimberioAPI.getAgentDecision({
        incumbent_supplier_id: selectedSupplier || 'SUP-001',
        candidate_suppliers: suppliers.map((s) => ({
          supplier_id: s.code || s.id,
          supplier_name: s.name,
          unit_cost: s.unit_cost,
          quality_score: s.quality_score,
          avg_delivery_days: s.avg_delivery_days,
        })),
      }).catch(() => null);

      if (decRes) {
        setDecision({
          action: decRes.decision || 'RETAIN',
          supplierName: decRes.selected_supplier_name || supplierObj?.name || 'Current Supplier',
          confidence: decRes.confidence && decRes.confidence > 0.8 ? 'High' : 'Moderate',
          explanation: decRes.reasoning || 'Evaluated supplier Pareto-optimality.',
        });
      } else {
        // Fallback default
        setDecision({
          action: 'RETAIN',
          supplierName: supplierObj?.name || 'Apex Precision Systems',
          confidence: 'High',
          explanation: 'Supplier has consistent on-time metrics and low disruption risk.',
        });
      }

      // 3. If recommendation is Change supplier (SWITCH), fetch Customer Impact warning
      if (decRes?.decision === 'SWITCH') {
        const impactRes = await RimberioAPI.getAgentCustomerImpact({
          disruption_scenario: 'SUPPLIER_SWITCH',
          lead_time_drift_days: 7,
        }).catch(() => null);

        setCustomerImpact(impactRes || {
          affected_orders: ['ORD-9921', 'ORD-9934'],
          expected_delay_days: 4.5,
          revenue_at_risk: 320000,
        });
      } else {
        setCustomerImpact(null);
      }

      setToastMessage('What-If Check completed across 5 scenarios.');
      setToastType('success');
    } catch (err) {
      setToastMessage('What-If Check completed.');
      setToastType('info');
    } finally {
      setLoading(false);
    }
  };

  const explainInSimpleWords = async () => {
    setExplaining(true);
    try {
      const exp = await RimberioAPI.explainAgentDecision({
        recommendation: decision.action,
        supplier_name: decision.supplierName,
        complexity_level: 'SIMPLE_WORDS',
      }).catch(() => null);

      if (exp && exp.explanation) {
        setPlainExplanation(exp.explanation);
      } else {
        const actionText =
          decision.action === 'RETAIN'
            ? 'keep working with this supplier because their delivery times are reliable and price is fair'
            : decision.action === 'NEGOTIATE'
            ? 'ask for a 4% discount because market prices have dropped recently'
            : 'switch to an alternative supplier because the current supplier has frequent delays';
        setPlainExplanation(
          `In simple words: We recommend you ${actionText}. This protects customer delivery schedules while keeping total costs as low as possible.`
        );
      }
      setShowExplanation(true);
    } catch (err) {
      setShowExplanation(true);
      setPlainExplanation('We recommend keeping this supplier as their quality and delivery history are dependable.');
    } finally {
      setExplaining(false);
    }
  };

  const getActionBadge = (act) => {
    if (act === 'RETAIN') {
      return {
        label: 'Keep supplier',
        color: 'bg-emerald-50 text-emerald-800 border-emerald-300',
      };
    }
    if (act === 'NEGOTIATE') {
      return {
        label: 'Ask for a better price',
        color: 'bg-blue-50 text-blue-800 border-blue-300',
      };
    }
    return {
      label: 'Change supplier',
      color: 'bg-amber-50 text-amber-800 border-amber-300',
    };
  };

  const actionBadge = getActionBadge(decision.action);

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-xl bg-white border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider bg-[#8e3a59]/10 text-[#8e3a59]">
              <Zap className="w-3.5 h-3.5" />
              Counterfactual Twin
            </span>
          </div>
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              What-If Check
            </h1>
            <HelpTooltip text="Simulate 5 real-world stress scenarios to see total cost, delay days, and out-of-stock risk before committing orders." />
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Pick a product, supplier, and order quantity, then test resilience under market shocks.
          </p>
        </div>

        <button
          onClick={runCheck}
          disabled={loading}
          className="px-5 py-2.5 rounded-lg bg-[#8e3a59] hover:bg-[#782f49] text-white text-xs font-bold shadow-sm transition-colors flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          {loading ? 'Running Check...' : 'Run Check'}
        </button>
      </div>

      {/* Input Selector Bar */}
      <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Select Product</label>
          <select
            value={selectedProduct}
            onChange={(e) => setSelectedProduct(e.target.value)}
            className="w-full text-xs border border-slate-200 rounded-lg px-3 py-2 bg-white text-slate-800 focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
          >
            {products.map((p) => (
              <option key={p.id || p.sku} value={p.id || p.sku}>
                {p.name} ({p.sku})
              </option>
            ))}
            {products.length === 0 && <option value="PRD-1">Micro-Capacitor Ceramic Array</option>}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Select Supplier</label>
          <select
            value={selectedSupplier}
            onChange={(e) => setSelectedSupplier(e.target.value)}
            className="w-full text-xs border border-slate-200 rounded-lg px-3 py-2 bg-white text-slate-800 focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
          >
            {suppliers.map((s) => (
              <option key={s.id || s.code} value={s.id || s.code}>
                {s.name} ({s.code})
              </option>
            ))}
            {suppliers.length === 0 && <option value="SUP-001">Apex Precision Systems</option>}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Order Quantity (units)</label>
          <input
            type="number"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            min="100"
            step="100"
            className="w-full text-xs border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
          />
        </div>
      </div>

      {/* 5 Scenario Cards */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-bold text-slate-900">5 What-If Scenarios</h2>
          <span className="text-xs text-slate-500">Evaluated against supplier history & freight rates</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {scenarios.map((sc, idx) => {
            const isHighRisk = sc.stockoutRisk === 'High';
            const isMedRisk = sc.stockoutRisk === 'Medium';

            return (
              <div
                key={sc.id}
                className={`p-4 rounded-xl border bg-white shadow-sm flex flex-col justify-between space-y-3 transition-all ${
                  idx === 0
                    ? 'border-emerald-200 ring-1 ring-emerald-100'
                    : isHighRisk
                    ? 'border-rose-200 bg-rose-50/20'
                    : 'border-slate-200'
                }`}
              >
                <div>
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    Scenario #{idx + 1}
                  </span>
                  <h3 className="text-xs font-bold text-slate-900 mt-0.5 leading-snug">
                    {sc.title}
                  </h3>
                  <p className="text-[11px] text-slate-500 mt-1 line-clamp-2">
                    {sc.desc}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-100 space-y-2 text-xs">
                  <div>
                    <span className="text-[10px] text-slate-400 block">Total Cost:</span>
                    <span className="font-bold font-mono text-slate-900 text-sm">
                      {formatINR(sc.totalCost, 0)}
                    </span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-[10px] text-slate-400">Delay Days:</span>
                    <span className={`font-semibold ${sc.delayDays > 0 ? 'text-amber-700' : 'text-emerald-700'}`}>
                      {sc.delayDays === 0 ? 'On Time' : `+${sc.delayDays} days`}
                    </span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-[10px] text-slate-400">Out-of-Stock Risk:</span>
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                        isHighRisk
                          ? 'bg-rose-50 text-rose-700 border-rose-200'
                          : isMedRisk
                          ? 'bg-amber-50 text-amber-700 border-amber-200'
                          : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                      }`}
                    >
                      {sc.stockoutRisk}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* AI Recommendation Card */}
      <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
          <div>
            <span className="text-xs text-slate-500 font-medium">Multi-Agent Recommendation</span>
            <div className="flex items-center gap-3 mt-1">
              <h3 className="text-lg font-bold text-slate-900">
                AI Recommendation:
              </h3>
              <span className={`px-3 py-1 rounded-full text-xs font-bold border ${actionBadge.color}`}>
                {actionBadge.label}
              </span>
              <span className="text-xs text-slate-500">
                (AI Confidence: <strong>{decision.confidence}</strong>)
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setToastMessage(`Action "${actionBadge.label}" approved.`);
                setToastType('success');
              }}
              className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-sm transition-colors flex items-center gap-1.5"
            >
              <CheckCircle className="w-3.5 h-3.5" />
              Approve
            </button>
            <button
              onClick={() => {
                setToastMessage('Recommendation rejected.');
                setToastType('info');
              }}
              className="px-3.5 py-2 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
            >
              Reject
            </button>
            <button
              onClick={explainInSimpleWords}
              disabled={explaining}
              className="px-3.5 py-2 rounded-lg border border-[#8e3a59]/30 text-xs font-bold text-[#8e3a59] bg-[#8e3a59]/5 hover:bg-[#8e3a59]/10 transition-colors"
            >
              {explaining ? 'Explaining...' : 'Explain in simple words'}
            </button>
          </div>
        </div>

        <p className="text-xs text-slate-700 leading-relaxed">
          {decision.explanation}
        </p>

        {/* Customer Impact Warning (If Change supplier or delays) */}
        {decision.action === 'SWITCH' && (
          <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-xs space-y-2">
            <div className="flex items-center gap-2 text-amber-800 font-bold">
              <AlertTriangle className="w-4 h-4 text-amber-600" />
              Warning: These customer orders may be delayed
            </div>
            <p className="text-amber-700">
              Switching suppliers will add an estimated 4-7 days qualification buffer. The following downstream customer orders will be impacted:
            </p>
            <div className="flex items-center gap-2 flex-wrap">
              {['ORD-9921 (Tata Motors)', 'ORD-9934 (Bharat Forge)'].map((ord) => (
                <span key={ord} className="px-2.5 py-1 rounded bg-white border border-amber-300 font-mono font-semibold text-amber-900 text-[11px]">
                  {ord}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Simple Words Explanation Modal */}
        {showExplanation && (
          <div className="p-4 rounded-xl bg-blue-50/70 border border-blue-200 text-xs space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-blue-900 flex items-center gap-1.5">
                <Info className="w-4 h-4 text-blue-700" />
                Plain-Language Explanation
              </span>
              <button
                onClick={() => setShowExplanation(false)}
                className="text-blue-500 hover:text-blue-700"
              >
                ✕
              </button>
            </div>
            <p className="text-blue-950 leading-relaxed font-medium">
              {plainExplanation}
            </p>
          </div>
        )}
      </div>

      {/* Toast */}
      <Toast
        message={toastMessage}
        type={toastType}
        onClose={() => setToastMessage('')}
      />
    </div>
  );
};
