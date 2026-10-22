/**
 * RIMBERIO Enterprise API Client
 * ===============================
 * All API calls go through this module.
 * Token is injected automatically from localStorage.
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000';

function getToken() {
  return localStorage.getItem('rimberio_token');
}

async function fetchJSON(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  try {
    const res = await fetch(url, { ...options, headers });
    if (res.status === 401) {
      // Token expired or invalid — clear and redirect to login
      localStorage.removeItem('rimberio_token');
      localStorage.removeItem('rimberio_user');
      window.dispatchEvent(new Event('rimberio_logout'));
      throw new Error('Session expired. Please log in again.');
    }
    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      throw new Error(errBody.detail || `HTTP ${res.status}: ${res.statusText}`);
    }
    return await res.json();
  } catch (err) {
    console.warn(`[RIMBERIO API] ${endpoint}:`, err.message);
    throw err;
  }
}

export const RimberioAPI = {
  // ─── Authentication ───
  login: (email, password) =>
    fetchJSON('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  register: (data) =>
    fetchJSON('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // ─── User Context (/me) ───
  getMe: () => fetchJSON('/api/v1/me'),
  getMyPermissions: () => fetchJSON('/api/v1/me/permissions'),
  getMyCapabilities: () => fetchJSON('/api/v1/me/capabilities'),
  getMyNavigation: () => fetchJSON('/api/v1/me/navigation'),

  // ─── Admin ───
  getAdminUsers: (params = '') => fetchJSON(`/api/v1/admin/users${params ? '?' + params : ''}`),
  createUser: (data) =>
    fetchJSON('/api/v1/admin/users', { method: 'POST', body: JSON.stringify(data) }),
  updateUser: (userId, data) =>
    fetchJSON(`/api/v1/admin/users/${userId}`, { method: 'PATCH', body: JSON.stringify(data) }),
  assignUserRole: (userId, roleId) =>
    fetchJSON(`/api/v1/admin/users/${userId}/roles`, {
      method: 'POST',
      body: JSON.stringify({ role_id: roleId }),
    }),

  getAdminDepartments: () => fetchJSON('/api/v1/admin/departments'),
  createDepartment: (data) =>
    fetchJSON('/api/v1/admin/departments', { method: 'POST', body: JSON.stringify(data) }),
  updateDepartment: (deptId, data) =>
    fetchJSON(`/api/v1/admin/departments/${deptId}`, { method: 'PATCH', body: JSON.stringify(data) }),

  getAdminRoles: () => fetchJSON('/api/v1/admin/roles'),
  createRole: (data) =>
    fetchJSON('/api/v1/admin/roles', { method: 'POST', body: JSON.stringify(data) }),

  getAdminPermissions: () => fetchJSON('/api/v1/admin/permissions'),
  getAdminAICapabilities: () => fetchJSON('/api/v1/admin/ai-capabilities'),
  getAdminOrganization: () => fetchJSON('/api/v1/admin/organization'),

  // ─── Health ───
  checkHealth: () => fetchJSON('/health'),

  // ─── Business Data (will be progressively protected) ───
  getSuppliers: () => fetchJSON('/api/v1/suppliers'),
  getProducts: () => fetchJSON('/api/v1/products'),
  getCustomers: () => fetchJSON('/api/v1/customers'),
  getRFQs: () => fetchJSON('/api/v1/rfqs'),
  getQuotations: () => fetchJSON('/api/v1/quotations'),
  getQuotes: () => fetchJSON('/api/v1/quotations'), // alias used by Procurement & Supplier pages
  getNegotiations: () => fetchJSON('/api/v1/negotiations'),
  getPurchaseOrders: () => fetchJSON('/api/v1/purchase-orders'),
  getInventory: () => fetchJSON('/api/v1/inventory'),
  getDemand: () => fetchJSON('/api/v1/demand'),
  getShipments: () => fetchJSON('/api/v1/shipments'),
  getQuality: () => fetchJSON('/api/v1/quality'),
  getRiskEvents: () => fetchJSON('/api/v1/risk'),
  getSimulations: () => fetchJSON('/api/v1/simulations'),
  getDecisions: () => fetchJSON('/api/v1/decisions'),
  getCustomerImpact: () => fetchJSON('/api/v1/customer-impact'),
  getCarriers: () => fetchJSON('/api/v1/carriers'),
  getCustomerOrders: () => fetchJSON('/api/v1/customer-orders'),
  getSupplierPerformance: () => fetchJSON('/api/v1/supplier-performance'),
  getWarehouses: () => fetchJSON('/api/v1/warehouses'),

  // ─── Supplier CRUD ───
  createSupplier: (data) =>
    fetchJSON('/api/suppliers', { method: 'POST', body: JSON.stringify(data) }),
  updateSupplier: (code, data) =>
    fetchJSON(`/api/suppliers/${code}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteSupplier: (code) =>
    fetchJSON(`/api/suppliers/${code}`, { method: 'DELETE' }),
  resetSuppliers: () =>
    fetchJSON('/api/suppliers/reset-kaggle', { method: 'POST' }),

  // ─── AI Agents & Workflow ───
  getAgentRegistry: () => fetchJSON('/api/agents/registry'),
  orchestrateWorkflow: (params) =>
    fetchJSON('/api/agents/orchestrate', { method: 'POST', body: JSON.stringify(params) }),
  evaluateAdaptiveDecision: (params) =>
    fetchJSON('/api/agents/decision', { method: 'POST', body: JSON.stringify(params) }),
  generateExplanation: (params) =>
    fetchJSON('/api/agents/explain', { method: 'POST', body: JSON.stringify(params) }),
  evaluateCustomerImpact: (params) =>
    fetchJSON('/api/agents/customer-impact', { method: 'POST', body: JSON.stringify(params) }),

  // ─── Negotiation Sessions ───
  getNegotiationSession: (sessionId = 'SES-AUTONOMOUS-01') =>
    fetchJSON(`/api/v1/negotiations/runtime/${sessionId}`),
  executeNegotiationStep: (params) =>
    fetchJSON('/api/v1/negotiations/runtime/step', { method: 'POST', body: JSON.stringify(params) }),
  startNegotiationSession: (params) =>
    fetchJSON('/api/agents/negotiate/start', { method: 'POST', body: JSON.stringify(params) }),

  // ─── Counterfactual Twin (CNT) ───
  getCNTScenarios: () => fetchJSON('/api/v1/cnt/scenarios'),
  runCNTSimulation: (params) =>
    fetchJSON('/api/v1/cnt/simulate', { method: 'POST', body: JSON.stringify(params) }),
  runSimulation: (params) =>
    fetchJSON('/api/simulation/counterfactual', { method: 'POST', body: JSON.stringify(params) }),

  // ─── Decision & Learning ───
  evaluateDecision: (params) =>
    fetchJSON('/api/decision/evaluate', { method: 'POST', body: JSON.stringify(params) }),
  getLearningMetrics: () => fetchJSON('/api/learning/metrics'),
  triggerRecalibration: () =>
    fetchJSON('/api/learning/recalibrate', { method: 'POST' }),
  getCustomizationProfile: () => fetchJSON('/api/customization/profile'),

  // ─── Products CRUD ───
  createProduct: (data) =>
    fetchJSON('/api/v1/products', { method: 'POST', body: JSON.stringify(data) }),

  // ─── Customer Impact & Orders ───
  getImpactedOrders: () => fetchJSON('/api/customer-impact/orders'),
  createCustomerOrder: (data) =>
    fetchJSON('/api/customer-impact/orders', { method: 'POST', body: JSON.stringify(data) }),
  deleteCustomerOrder: (orderId) =>
    fetchJSON(`/api/customer-impact/orders/${orderId}`, { method: 'DELETE' }),
  resetSuppliersToKaggle: () =>
    fetchJSON('/api/suppliers/reset-kaggle', { method: 'POST' }),
  // ─── Dashboard Summary & Activity ───
  getDashboardSummary: (role) => fetchJSON(`/api/v1/dashboard/summary?role=${encodeURIComponent(role || 'BUYER')}`),
  getActivityLogs: (search = '') => fetchJSON(`/api/v1/activity-logs${search ? '?search=' + encodeURIComponent(search) : ''}`),

  // ─── Admin User Actions & Agents ───
  deleteUser: (userId) => fetchJSON(`/api/v1/admin/users/${userId}`, { method: 'DELETE' }),
  toggleUserStatus: (userId) => fetchJSON(`/api/v1/admin/users/${userId}/status`, { method: 'PATCH' }),
  resetUserPassword: (userId) => fetchJSON(`/api/v1/admin/users/${userId}/reset-password`, { method: 'POST' }),
  deleteDepartment: (deptId) => fetchJSON(`/api/v1/admin/departments/${deptId}`, { method: 'DELETE' }),
  getAIAgents: () => fetchJSON('/api/v1/admin/ai-agents'),
  toggleAIAgent: (agentId) => fetchJSON(`/api/v1/admin/ai-agents/${agentId}/toggle`, { method: 'PATCH' }),

  // ─── Products CRUD ───
  createProduct: (data) => fetchJSON('/api/v1/products', { method: 'POST', body: JSON.stringify(data) }),
  updateProduct: (id, data) => fetchJSON(`/api/v1/products/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteProduct: (id) => fetchJSON(`/api/v1/products/${id}`, { method: 'DELETE' }),

  // ─── Warehouses & Carriers ───
  createWarehouse: (data) => fetchJSON('/api/v1/warehouses', { method: 'POST', body: JSON.stringify(data) }),
  updateWarehouse: (id, data) => fetchJSON(`/api/v1/warehouses/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteWarehouse: (id) => fetchJSON(`/api/v1/warehouses/${id}`, { method: 'DELETE' }),
  createCarrier: (data) => fetchJSON('/api/v1/carriers', { method: 'POST', body: JSON.stringify(data) }),
  updateCarrier: (id, data) => fetchJSON(`/api/v1/carriers/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteCarrier: (id) => fetchJSON(`/api/v1/carriers/${id}`, { method: 'DELETE' }),

  // ─── Price Requests (RFQs) & Quotes ───
  createRFQ: (data) => fetchJSON('/api/v1/rfqs', { method: 'POST', body: JSON.stringify(data) }),
  deleteRFQ: (id) => fetchJSON(`/api/v1/rfqs/${id}`, { method: 'DELETE' }),
  submitQuotation: (data) => fetchJSON('/api/v1/quotations', { method: 'POST', body: JSON.stringify(data) }),
  updateQuotationStatus: (id, status) => fetchJSON(`/api/v1/quotations/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status }) }),
  deleteQuotation: (id) => fetchJSON(`/api/v1/quotations/${id}`, { method: 'DELETE' }),

  // ─── Purchase Orders ───
  createPurchaseOrder: (data) => fetchJSON('/api/v1/purchase-orders', { method: 'POST', body: JSON.stringify(data) }),
  updatePOStatus: (id, status) => fetchJSON(`/api/v1/purchase-orders/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status }) }),
  deletePurchaseOrder: (id) => fetchJSON(`/api/v1/purchase-orders/${id}`, { method: 'DELETE' }),

  // ─── Shipments ───
  createShipment: (data) => fetchJSON('/api/v1/shipments', { method: 'POST', body: JSON.stringify(data) }),
  updateShipmentStatus: (id, payload) => fetchJSON(`/api/v1/shipments/${id}/status`, { method: 'PATCH', body: JSON.stringify(payload) }),
  deleteShipment: (id) => fetchJSON(`/api/v1/shipments/${id}`, { method: 'DELETE' }),

  // ─── Stock & Movements ───
  getWarehouseStock: (whId) => fetchJSON(`/api/v1/stock${whId ? '?warehouse_id=' + whId : ''}`),
  recordStockMovement: (data) => fetchJSON('/api/v1/stock/movements', { method: 'POST', body: JSON.stringify(data) }),

  // ─── Customer Self-Service & Notices ───
  cancelCustomerOrder: (id) => fetchJSON(`/api/v1/customer-orders/${id}`, { method: 'DELETE' }),
  getCustomerNotices: () => fetchJSON('/api/v1/customer-notices'),
  markNoticeRead: (id) => fetchJSON(`/api/v1/customer-notices/${id}/read`, { method: 'PATCH' }),
  deleteCustomerNotice: (id) => fetchJSON(`/api/v1/customer-notices/${id}`, { method: 'DELETE' }),

  // ─── Support Tickets ───
  getSupportTickets: () => fetchJSON('/api/v1/support-tickets'),
  createSupportTicket: (data) => fetchJSON('/api/v1/support-tickets', { method: 'POST', body: JSON.stringify(data) }),
  closeSupportTicket: (id) => fetchJSON(`/api/v1/support-tickets/${id}/close`, { method: 'PATCH' }),

  // ─── Negotiations & Price Talks ───
  getNegotiationSession: (sessionId = 'SES-AUTONOMOUS-01') =>
    fetchJSON(`/api/v1/negotiations/runtime/${sessionId}`).catch(() =>
      fetchJSON(`/api/agents/negotiate/session/${sessionId}`)
    ),
  startNegotiation: (payload) =>
    fetchJSON('/api/v1/negotiations/runtime/start', { method: 'POST', body: JSON.stringify(payload) }).catch(() =>
      fetchJSON(`/api/agents/negotiate/start?supplier_code=${encodeURIComponent(payload.supplier_code || 'SUP-001')}&supplier_name=${encodeURIComponent(payload.supplier_name || 'Apex Global')}&sku_code=${encodeURIComponent(payload.sku_code || 'SKU-MC-772')}`, { method: 'POST' })
    ),
  stepNegotiation: (payload) =>
    fetchJSON('/api/v1/negotiations/runtime/step', { method: 'POST', body: JSON.stringify(payload) }).catch(() =>
      fetchJSON('/api/agents/negotiate/step', { method: 'POST', body: JSON.stringify(payload) })
    ),

  // ─── Counterfactual Twin & Multi-Agent Decisions ───
  simulateCNT: (payload) => fetchJSON('/api/v1/cnt/simulate', { method: 'POST', body: JSON.stringify(payload) }),
  getAgentDecision: (payload) => fetchJSON('/api/agents/decision', { method: 'POST', body: JSON.stringify(payload) }),
  explainAgentDecision: (payload) => fetchJSON('/api/agents/explain', { method: 'POST', body: JSON.stringify(payload) }),
  getAgentCustomerImpact: (payload) => fetchJSON('/api/agents/customer-impact', { method: 'POST', body: JSON.stringify(payload) }),
  notifyCustomerImpactBatch: (payload) => fetchJSON('/api/customer-impact/notify/batch', { method: 'POST', body: JSON.stringify(payload) }),
};


