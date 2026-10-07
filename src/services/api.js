/**
 * RIMBERIO Enterprise API Client
 * Connects frontend React components to the FastAPI Python backend with real-time fallbacks.
 */

const API_BASE = 'http://127.0.0.1:8000';

async function fetchJSON(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
    });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    return await res.json();
  } catch (err) {
    console.warn(`[RIMBERIO API] Request failed for ${endpoint}:`, err.message);
    throw err;
  }
}

export const RimberioAPI = {
  // ─── Health & Telemetry ───
  checkHealth: () => fetchJSON('/health'),

  // ─── Suppliers ───
  getSuppliers: () => fetchJSON('/api/suppliers'),

  // ─── Customer Impact & Notices ───
  getImpactedOrders: () => fetchJSON('/api/customer-impact/orders'),
  dispatchBatchNotices: (orderIds, reason = 'Global maritime route transit delay') =>
    fetchJSON('/api/customer-impact/notify/batch', {
      method: 'POST',
      body: JSON.stringify({ order_ids: orderIds, disruption_reason: reason }),
    }),

  // ─── Counterfactual Simulation ───
  runSimulation: (params) =>
    fetchJSON('/api/simulation/counterfactual', {
      method: 'POST',
      body: JSON.stringify(params),
    }),

  // ─── Multi-Agent Autonomous Negotiation ───
  getNegotiationSession: (sessionId = 'SES-AUTONOMOUS-01') =>
    fetchJSON(`/api/agents/negotiate/session/${sessionId}`),
  executeNegotiationStep: (params) =>
    fetchJSON('/api/agents/negotiate/step', {
      method: 'POST',
      body: JSON.stringify(params),
    }),

  // ─── Adaptive Decision Center ───
  evaluateDecision: (params) =>
    fetchJSON('/api/decision/evaluate', {
      method: 'POST',
      body: JSON.stringify(params),
    }),

  // ─── Learning Loop & Confusion Matrix ───
  getLearningMetrics: () => fetchJSON('/api/learning/metrics'),
  triggerRecalibration: () =>
    fetchJSON('/api/learning/recalibrate', {
      method: 'POST',
    }),

  // ─── Customization Control Plane ───
  getCustomizationProfile: () => fetchJSON('/api/customization/profile'),
  updateCriteriaWeights: (weights) =>
    fetchJSON('/api/customization/weights', {
      method: 'PATCH',
      body: JSON.stringify(weights),
    }),

  // ─── Kaggle Datasets & Benchmarks ───
  getKaggleSummary: () => fetchJSON('/api/data/kaggle/summary'),
  getKaggleDataCoSample: () => fetchJSON('/api/data/kaggle/dataco-sample'),
  getKaggleSupplyChainSample: () => fetchJSON('/api/data/kaggle/supplychain-sample'),
};
