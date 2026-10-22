import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { RimberioAPI } from '../services/api';
import { formatINR } from '../utils/currency';
import {
  ShoppingBag,
  MapPin,
  RefreshCw,
  Search,
  Plus,
  HelpCircle,
  X,
  CheckCircle,
  Truck,
  Clock,
  AlertTriangle,
  MessageSquare,
  Bell,
  Check,
  Trash2,
  Edit2,
  Package,
} from 'lucide-react';
import {
  HelpTooltip,
  StatusBadge,
  DeleteConfirmDialog,
  EmptyState,
  Toast,
} from '../components/common/CommonUI';

export const CustomerPortalPage = ({ initialTab = 'orders' }) => {
  const { user, setCurrentPage } = useApp();
  const [activeTab, setActiveTab] = useState(initialTab);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');

  // Customer Data
  const [orders, setOrders] = useState([]);
  const [notices, setNotices] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [products, setProducts] = useState([]);

  // Selected order for tracking tab
  const [selectedTrackingOrderId, setSelectedTrackingOrderId] = useState('');

  // Modals
  const [showOrderModal, setShowOrderModal] = useState(false);
  const [editingOrder, setEditingOrder] = useState(null);
  const [orderForm, setOrderForm] = useState({
    product_name: '',
    quantity: 1000,
    needed_by: new Date(Date.now() + 10 * 86400000).toISOString().split('T')[0],
  });

  const [showTicketModal, setShowTicketModal] = useState(false);
  const [ticketForm, setTicketForm] = useState({
    subject: '',
    message: '',
  });

  // Delete Dialog
  const [deleteDialog, setDeleteDialog] = useState({
    isOpen: false,
    itemType: '',
    item: null,
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const [ordRes, notRes, tktRes, prdRes] = await Promise.all([
        RimberioAPI.getCustomerOrders().catch(() => []),
        RimberioAPI.getCustomerNotices().catch(() => []),
        RimberioAPI.getSupportTickets().catch(() => []),
        RimberioAPI.getProducts().catch(() => []),
      ]);

      const oList = Array.isArray(ordRes) ? ordRes : [];
      const nList = Array.isArray(notRes) ? notRes : [];
      const tList = Array.isArray(tktRes) ? tktRes : [];
      const pList = Array.isArray(prdRes) ? prdRes : [];

      setOrders(oList);
      setNotices(nList);
      setTickets(tList);
      setProducts(pList);

      if (oList.length > 0 && !selectedTrackingOrderId) {
        setSelectedTrackingOrderId(oList[0].id || oList[0].order_id || oList[0].order_number);
      }
    } catch (err) {
      setToastMessage('Error loading customer portal data');
      setToastType('error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (initialTab) setActiveTab(initialTab);
  }, [initialTab]);

  // Order Actions
  const handleOpenAddOrder = () => {
    setEditingOrder(null);
    setOrderForm({
      product_name: products[0]?.name || 'Micro-Capacitor Ceramic Array',
      quantity: 1000,
      needed_by: new Date(Date.now() + 10 * 86400000).toISOString().split('T')[0],
    });
    setShowOrderModal(true);
  };

  const handleOpenEditOrder = (ord) => {
    setEditingOrder(ord);
    setOrderForm({
      product_name: ord.product_name,
      quantity: ord.quantity,
      needed_by: ord.promised_delivery_date || '',
    });
    setShowOrderModal(true);
  };

  const handleSaveOrder = async (e) => {
    e.preventDefault();
    try {
      if (editingOrder) {
        await RimberioAPI.createCustomerOrder({
          ...editingOrder,
          product_name: orderForm.product_name,
          quantity: parseInt(orderForm.quantity, 10),
          promised_delivery_date: orderForm.needed_by,
        });
        setToastMessage(`Order ${editingOrder.order_number || editingOrder.id} updated.`);
      } else {
        const ordId = `ORD-IN-${Math.floor(1000 + Math.random() * 9000)}`;
        await RimberioAPI.createCustomerOrder({
          order_id: ordId,
          order_number: ordId,
          customer_name: user?.full_name || 'Valued Customer',
          contact_email: user?.email || 'customer@enterprise.com',
          product_name: orderForm.product_name,
          quantity: parseInt(orderForm.quantity, 10),
          unit_price: 165.0,
          order_value: parseInt(orderForm.quantity, 10) * 165.0,
          promised_delivery_date: orderForm.needed_by,
          status: 'ORDERED',
        });
        setToastMessage(`Order ${ordId} placed successfully.`);
      }
      setToastType('success');
      setShowOrderModal(false);
      loadData();
    } catch (err) {
      setToastMessage(err.message || 'Operation failed');
      setToastType('error');
    }
  };

  const handleCancelOrder = async (ord) => {
    try {
      await RimberioAPI.cancelCustomerOrder(ord.id || ord.order_id);
      setToastMessage(`Order ${ord.order_number || ord.id} has been cancelled.`);
      setToastType('success');
      loadData();
    } catch (err) {
      setToastMessage(err.message || 'Failed to cancel order');
      setToastType('error');
    }
  };

  // Notice Actions
  const handleMarkNoticeRead = async (noticeId) => {
    try {
      await RimberioAPI.markNoticeRead(noticeId);
      setToastMessage('Notice marked as read.');
      setToastType('success');
      loadData();
    } catch (err) {
      setToastMessage('Could not update notice');
      setToastType('error');
    }
  };

  const handleDeleteNotice = async (noticeId) => {
    try {
      await RimberioAPI.deleteCustomerNotice(noticeId);
      setToastMessage('Notice deleted.');
      setToastType('success');
      loadData();
    } catch (err) {
      setToastMessage('Failed to delete notice');
      setToastType('error');
    }
  };

  // Ticket Actions
  const handleCreateTicket = async (e) => {
    e.preventDefault();
    try {
      await RimberioAPI.createSupportTicket({
        customer_id: user?.email || 'customer',
        subject: ticketForm.subject,
        message: ticketForm.message,
      });
      setToastMessage('Support ticket created. Support team will respond shortly.');
      setToastType('success');
      setShowTicketModal(false);
      setTicketForm({ subject: '', message: '' });
      loadData();
    } catch (err) {
      setToastMessage(err.message || 'Failed to create ticket');
      setToastType('error');
    }
  };

  const handleCloseTicket = async (tktId) => {
    try {
      await RimberioAPI.closeSupportTicket(tktId);
      setToastMessage('Support ticket closed.');
      setToastType('success');
      loadData();
    } catch (err) {
      setToastMessage(err.message || 'Failed to close ticket');
      setToastType('error');
    }
  };

  // Selected Order for Tracking
  const trackingOrder = orders.find(
    (o) => (o.id || o.order_id || o.order_number) === selectedTrackingOrderId
  ) || orders[0];

  const trackingSteps = [
    { label: 'Ordered', step: 1 },
    { label: 'Packed', step: 2 },
    { label: 'Shipped', step: 3 },
    { label: 'Out for Delivery', step: 4 },
    { label: 'Delivered', step: 5 },
  ];

  const getTrackingStepIndex = (status) => {
    const s = (status || '').toUpperCase();
    if (s.includes('DELIVER') || s.includes('COMPLET')) return 5;
    if (s.includes('OUT') || s.includes('NEAR')) return 4;
    if (s.includes('SHIP') || s.includes('TRANSIT')) return 3;
    if (s.includes('PACK') || s.includes('PREPAR') || s.includes('APPROV')) return 2;
    return 1;
  };

  const currentStep = getTrackingStepIndex(trackingOrder?.status);

  // Stats
  const activeOrdersCount = orders.filter((o) => !o.status?.includes('DELIVER') && !o.status?.includes('CANCEL')).length;
  const deliveredOrdersCount = orders.filter((o) => o.status?.includes('DELIVER')).length;
  const delayedOrdersCount = orders.filter((o) => o.status?.includes('DELAY') || o.status?.includes('HOLD')).length;
  const openTicketsCount = tickets.filter((t) => t.status === 'OPEN' || t.status === 'IN_PROGRESS').length;

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-xl bg-white border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider bg-[#8e3a59]/10 text-[#8e3a59]">
              <ShoppingBag className="w-3.5 h-3.5" />
              Customer Orders & Deliveries
            </span>
          </div>
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              {activeTab === 'orders'
                ? 'My Orders'
                : activeTab === 'tracking'
                ? 'Order Tracking'
                : activeTab === 'notifications'
                ? 'Notifications'
                : 'Customer Support'}
            </h1>
            <HelpTooltip text="Track live shipment progress, view order statuses, receive plain delay notices, and request assistance." />
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Fulfillment portal for {user?.full_name || 'Boeing Commercial Procurement'}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadData}
            disabled={loading}
            className="px-3.5 py-2 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 transition-colors flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          {activeTab === 'orders' && (
            <button
              onClick={handleOpenAddOrder}
              className="px-4 py-2 rounded-lg bg-[#8e3a59] hover:bg-[#782f49] text-white text-xs font-bold shadow-sm transition-colors flex items-center gap-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              + Place New Order
            </button>
          )}
          {activeTab === 'support' && (
            <button
              onClick={() => setShowTicketModal(true)}
              className="px-4 py-2 rounded-lg bg-[#8e3a59] hover:bg-[#782f49] text-white text-xs font-bold shadow-sm transition-colors flex items-center gap-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              + New Ticket
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2 overflow-x-auto">
        {[
          { id: 'orders', label: `My Orders (${orders.length})`, icon: ShoppingBag },
          { id: 'tracking', label: 'Order Tracking', icon: Truck },
          { id: 'notifications', label: `Notifications (${notices.length})`, icon: Bell },
          { id: 'support', label: `Support (${tickets.length})`, icon: MessageSquare },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3.5 py-2 rounded-lg text-xs font-bold flex items-center gap-2 whitespace-nowrap transition-all ${
                isActive
                  ? 'bg-[#8e3a59] text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* 4 Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Active Orders</span>
          <div className="text-2xl font-bold text-slate-900 mt-1">{activeOrdersCount}</div>
          <p className="text-[11px] text-slate-400 mt-0.5">In production & transit</p>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Delivered Orders</span>
          <div className="text-2xl font-bold text-emerald-700 mt-1">{deliveredOrdersCount}</div>
          <p className="text-[11px] text-slate-400 mt-0.5">Successfully fulfilled</p>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Delayed Orders</span>
          <div className="text-2xl font-bold text-amber-700 mt-1">{delayedOrdersCount}</div>
          <p className="text-[11px] text-slate-400 mt-0.5">Corridor drift alerts</p>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Open Support Tickets</span>
          <div className="text-2xl font-bold text-blue-700 mt-1">{openTicketsCount}</div>
          <p className="text-[11px] text-slate-400 mt-0.5">Active inquiries</p>
        </div>
      </div>

      {/* ── TAB 1: MY ORDERS ── */}
      {activeTab === 'orders' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
            <div className="relative w-full sm:w-80">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search orders..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
              />
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 font-bold uppercase text-[11px] border-b border-slate-200">
                  <tr>
                    <th className="px-5 py-3.5">Order Number</th>
                    <th className="px-5 py-3.5">Product</th>
                    <th className="px-5 py-3.5">Quantity</th>
                    <th className="px-5 py-3.5">Needed By</th>
                    <th className="px-5 py-3.5">Status</th>
                    <th className="px-5 py-3.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {orders
                    .filter((o) =>
                      (o.order_number || o.order_id || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                      (o.product_name || '').toLowerCase().includes(searchTerm.toLowerCase())
                    )
                    .map((ord) => {
                      const isPreShipping = !ord.status?.includes('SHIP') && !ord.status?.includes('DELIVER');

                      return (
                        <tr key={ord.id || ord.order_id} className="hover:bg-slate-50/60 transition-colors">
                          <td className="px-5 py-3.5 font-mono font-bold text-slate-900">
                            {ord.order_number || ord.order_id}
                          </td>
                          <td className="px-5 py-3.5 font-semibold text-slate-800">
                            {ord.product_name || 'Precision Micro-Capacitor'}
                          </td>
                          <td className="px-5 py-3.5 font-mono text-slate-700">
                            {(ord.quantity || 1000).toLocaleString()} units
                          </td>
                          <td className="px-5 py-3.5 text-slate-600 font-medium">
                            {ord.promised_delivery_date || 'Under review'}
                          </td>
                          <td className="px-5 py-3.5">
                            <StatusBadge status={ord.status} />
                          </td>
                          <td className="px-5 py-3.5 text-right space-x-1.5">
                            <button
                              onClick={() => {
                                setSelectedTrackingOrderId(ord.id || ord.order_id || ord.order_number);
                                setActiveTab('tracking');
                              }}
                              className="px-2.5 py-1 text-xs font-semibold text-blue-700 hover:bg-blue-50 rounded border border-blue-200"
                            >
                              Track
                            </button>
                            {isPreShipping && (
                              <button
                                onClick={() => handleOpenEditOrder(ord)}
                                className="px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded border border-slate-200"
                              >
                                Edit
                              </button>
                            )}
                            {isPreShipping && (
                              <button
                                onClick={() => handleCancelOrder(ord)}
                                className="px-2.5 py-1 text-xs font-semibold text-rose-600 hover:bg-rose-50 rounded border border-rose-200"
                              >
                                Cancel Order
                              </button>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                </tbody>
              </table>
            </div>

            {orders.length === 0 && !loading && (
              <div className="p-8">
                <EmptyState
                  message="No orders placed yet."
                  actionLabel="+ Create your first order"
                  onAction={handleOpenAddOrder}
                />
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── TAB 2: ORDER TRACKING ── */}
      {activeTab === 'tracking' && (
        <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-sm space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">Live Order Fulfillment Tracking</h3>
              <p className="text-xs text-slate-500">Milestone timeline from factory order to delivery</p>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-700">Select Order:</span>
              <select
                value={selectedTrackingOrderId}
                onChange={(e) => setSelectedTrackingOrderId(e.target.value)}
                className="text-xs border border-slate-200 rounded-lg px-3 py-2 bg-white text-slate-800 font-bold focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
              >
                {orders.map((o) => (
                  <option key={o.id || o.order_id} value={o.id || o.order_id || o.order_number}>
                    {o.order_number || o.order_id} - {o.product_name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {trackingOrder ? (
            <div className="space-y-6">
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Tracking Order</span>
                  <h4 className="text-base font-bold text-slate-900 mt-0.5">{trackingOrder.order_number || trackingOrder.order_id}</h4>
                  <p className="text-xs text-slate-600">{trackingOrder.product_name} · {(trackingOrder.quantity || 1000).toLocaleString()} units</p>
                </div>

                <div className="text-right">
                  <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Expected Delivery</span>
                  <span className="text-sm font-bold text-slate-900 font-mono block mt-0.5">
                    {trackingOrder.promised_delivery_date || '2026-10-28'}
                  </span>
                  <StatusBadge status={trackingOrder.status} />
                </div>
              </div>

              {/* Step Bar */}
              <div className="py-6 px-4">
                <div className="relative flex items-center justify-between">
                  <div className="absolute left-0 top-1/2 -translate-y-1/2 w-full h-1 bg-slate-200 -z-0" />
                  <div
                    className="absolute left-0 top-1/2 -translate-y-1/2 h-1 bg-[#8e3a59] transition-all -z-0"
                    style={{ width: `${((currentStep - 1) / (trackingSteps.length - 1)) * 100}%` }}
                  />

                  {trackingSteps.map((step) => {
                    const isPassed = step.step <= currentStep;
                    const isCurrent = step.step === currentStep;

                    return (
                      <div key={step.step} className="flex flex-col items-center relative z-10">
                        <div
                          className={`w-9 h-9 rounded-full flex items-center justify-center font-bold text-xs transition-all ${
                            isPassed
                              ? 'bg-[#8e3a59] text-white shadow-md'
                              : 'bg-white border-2 border-slate-300 text-slate-400'
                          }`}
                        >
                          {isPassed ? <Check className="w-4 h-4" /> : step.step}
                        </div>
                        <span
                          className={`text-xs mt-2 font-semibold ${
                            isCurrent ? 'text-[#8e3a59] font-bold' : isPassed ? 'text-slate-800' : 'text-slate-400'
                          }`}
                        >
                          {step.label}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ) : (
            <EmptyState message="No order selected for tracking." />
          )}
        </div>
      )}

      {/* ── TAB 3: NOTIFICATIONS ── */}
      {activeTab === 'notifications' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Plain-Language Delivery Updates</h3>
              <p className="text-xs text-slate-500">Transparent delay notices and arrival confirmations</p>
            </div>
            <span className="text-xs text-slate-400">{notices.length} updates</span>
          </div>

          <div className="space-y-3">
            {notices.map((n) => (
              <div
                key={n.id}
                className={`p-4 rounded-xl border transition-all ${
                  n.is_read ? 'bg-white border-slate-200' : 'bg-blue-50/40 border-blue-200 ring-1 ring-blue-100'
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-amber-50 text-amber-700 flex items-center justify-center shrink-0 mt-0.5">
                      <Clock className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-slate-900 leading-snug">{n.title}</h4>
                      <p className="text-xs text-slate-700 mt-1 leading-relaxed">{n.message}</p>
                      <span className="text-[10px] text-slate-400 font-mono mt-1.5 block">{n.created_at || 'Recent'}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => {
                        setToastMessage('New expected delivery date accepted.');
                        setToastType('success');
                        handleMarkNoticeRead(n.id);
                      }}
                      className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-sm whitespace-nowrap"
                    >
                      Accept New Date
                    </button>
                    <button
                      onClick={() => setActiveTab('support')}
                      className="px-3 py-1.5 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 text-xs font-semibold whitespace-nowrap"
                    >
                      Contact Support
                    </button>
                    <button
                      onClick={() => handleDeleteNotice(n.id)}
                      className="p-1.5 text-slate-400 hover:text-rose-600 rounded"
                      title="Delete notice"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}

            {notices.length === 0 && (
              <div className="p-8 bg-white rounded-xl border border-slate-200 text-center text-slate-500 text-xs">
                No delivery alerts or notifications. All orders are running on schedule.
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── TAB 4: SUPPORT ── */}
      {activeTab === 'support' && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-100 flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900">Support Inquiries & Tickets</h3>
              <button
                onClick={() => setShowTicketModal(true)}
                className="px-3.5 py-1.5 rounded-lg bg-[#8e3a59] hover:bg-[#782f49] text-white text-xs font-bold shadow-sm flex items-center gap-1.5"
              >
                <Plus className="w-3.5 h-3.5" />
                + New Ticket
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 font-bold uppercase text-[11px] border-b border-slate-200">
                  <tr>
                    <th className="px-5 py-3.5">Subject</th>
                    <th className="px-5 py-3.5">Message</th>
                    <th className="px-5 py-3.5">Date</th>
                    <th className="px-5 py-3.5">Status</th>
                    <th className="px-5 py-3.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {tickets.map((tkt) => (
                    <tr key={tkt.id} className="hover:bg-slate-50/60 transition-colors">
                      <td className="px-5 py-3.5 font-bold text-slate-900">{tkt.subject}</td>
                      <td className="px-5 py-3.5 text-slate-600 max-w-xs truncate">{tkt.message}</td>
                      <td className="px-5 py-3.5 text-slate-500">{tkt.created_at || 'Recent'}</td>
                      <td className="px-5 py-3.5"><StatusBadge status={tkt.status} /></td>
                      <td className="px-5 py-3.5 text-right">
                        {tkt.status !== 'CLOSED' && (
                          <button
                            onClick={() => handleCloseTicket(tkt.id)}
                            className="px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded border border-slate-200"
                          >
                            Close Ticket
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                  {tickets.length === 0 && (
                    <tr>
                      <td colSpan={5} className="px-5 py-6 text-center text-slate-500">
                        No support tickets opened. Click "+ New Ticket" if you need assistance.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Place / Edit Order Modal */}
      {showOrderModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="w-full max-w-md bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">
                {editingOrder ? 'Edit Order' : '+ Place New Order'}
              </h3>
              <button onClick={() => setShowOrderModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSaveOrder} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Select Product</label>
                <select
                  value={orderForm.product_name}
                  onChange={(e) => setOrderForm({ ...orderForm, product_name: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                >
                  {products.map((p) => (
                    <option key={p.id || p.sku} value={p.name}>
                      {p.name} ({p.sku})
                    </option>
                  ))}
                  {products.length === 0 && (
                    <option value="Micro-Capacitor Ceramic Array">Micro-Capacitor Ceramic Array</option>
                  )}
                </select>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Quantity Needed</label>
                <input
                  type="number"
                  min="1"
                  value={orderForm.quantity}
                  onChange={(e) => setOrderForm({ ...orderForm, quantity: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Needed-By Date</label>
                <input
                  type="date"
                  value={orderForm.needed_by}
                  onChange={(e) => setOrderForm({ ...orderForm, needed_by: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowOrderModal(false)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-100 border border-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-[#8e3a59] hover:bg-[#782f49] shadow-sm"
                >
                  Confirm Order
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Support Ticket Modal */}
      {showTicketModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="w-full max-w-md bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">+ New Support Ticket</h3>
              <button onClick={() => setShowTicketModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateTicket} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Subject</label>
                <input
                  type="text"
                  placeholder="e.g. Inquire about revised delivery schedule for Order #1001"
                  value={ticketForm.subject}
                  onChange={(e) => setTicketForm({ ...ticketForm, subject: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Message</label>
                <textarea
                  rows="4"
                  placeholder="Describe your inquiry or requested support..."
                  value={ticketForm.message}
                  onChange={(e) => setTicketForm({ ...ticketForm, message: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowTicketModal(false)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-100 border border-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-[#8e3a59] hover:bg-[#782f49] shadow-sm"
                >
                  Submit Ticket
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Dialog */}
      <DeleteConfirmDialog
        isOpen={deleteDialog.isOpen}
        itemName={deleteDialog.item?.order_number || 'this item'}
        onConfirm={() => {}}
        onCancel={() => setDeleteDialog({ isOpen: false, itemType: '', item: null })}
      />

      {/* Toast */}
      <Toast
        message={toastMessage}
        type={toastType}
        onClose={() => setToastMessage('')}
      />
    </div>
  );
};
