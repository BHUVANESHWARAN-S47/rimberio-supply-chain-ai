import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { RimberioAPI } from '../services/api';
import {
  HelpTooltip,
  StatusBadge,
  Toast,
  AIAssistantCard,
} from '../components/common/CommonUI';
import {
  Users,
  Search,
  ShoppingCart,
  Activity,
  FileText,
  MessageSquare,
  DollarSign,
  Truck,
  Clock,
  Building,
  Ship,
  ShoppingBag,
  MapPin,
  Bell,
  HelpCircle,
  ArrowRight,
  RefreshCw,
} from 'lucide-react';

export const DashboardPage = () => {
  const { user, setCurrentPage } = useApp();
  const [summary, setSummary] = useState(null);
  const [activityLogs, setActivityLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toastMessage, setToastMessage] = useState('');

  const role = user?.role || 'BUYER';
  const roleUpper = role.toUpperCase();

  const loadData = async () => {
    setLoading(true);
    try {
      const [sumRes, actRes] = await Promise.all([
        RimberioAPI.getDashboardSummary(role).catch(() => null),
        RimberioAPI.getActivityLogs().catch(() => []),
      ]);
      setSummary(sumRes);
      setActivityLogs(Array.isArray(actRes) ? actRes.slice(0, 5) : []);
    } catch (err) {
      console.warn('[DashboardPage] Error loading dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [user]);

  // Card click navigations
  const handleCardClick = (cardIndex) => {
    if (roleUpper === 'ADMIN') {
      if (cardIndex === 1) setCurrentPage('admin_users');
      else if (cardIndex === 2) setCurrentPage('suppliers');
      else if (cardIndex === 3) setCurrentPage('suppliers');
      else if (cardIndex === 4) setCurrentPage('ai_health');
    } else if (roleUpper === 'BUYER' || roleUpper === 'PROCUREMENT_MANAGER') {
      if (cardIndex === 1) setCurrentPage('rfqs');
      else if (cardIndex === 2) setCurrentPage('negotiations');
      else if (cardIndex === 3) setCurrentPage('purchase_orders');
      else if (cardIndex === 4) setCurrentPage('purchase_orders');
    } else if (roleUpper === 'LOGISTICS_MANAGER' || roleUpper === 'SUPPLY_CHAIN_ANALYST') {
      if (cardIndex === 1) setCurrentPage('shipments');
      else if (cardIndex === 2) setCurrentPage('delays');
      else if (cardIndex === 3) setCurrentPage('warehouses');
      else if (cardIndex === 4) setCurrentPage('carriers');
    } else if (roleUpper === 'SUPPLIER') {
      if (cardIndex === 1) setCurrentPage('rfqs');
      else if (cardIndex === 2) setCurrentPage('rfqs');
      else if (cardIndex === 3) setCurrentPage('orders_to_deliver');
      else if (cardIndex === 4) setCurrentPage('orders_to_deliver');
    } else {
      // CUSTOMER
      if (cardIndex === 1) setCurrentPage('my_orders');
      else if (cardIndex === 2) setCurrentPage('my_orders');
      else if (cardIndex === 3) setCurrentPage('order_tracking');
      else if (cardIndex === 4) setCurrentPage('support');
    }
  };

  // Icon mapping for cards
  const getCardIcon = (index) => {
    if (roleUpper === 'ADMIN') {
      return [Users, Search, ShoppingCart, Activity][index - 1] || Users;
    } else if (roleUpper === 'BUYER' || roleUpper === 'PROCUREMENT_MANAGER') {
      return [FileText, MessageSquare, ShoppingCart, DollarSign][index - 1] || FileText;
    } else if (roleUpper === 'LOGISTICS_MANAGER' || roleUpper === 'SUPPLY_CHAIN_ANALYST') {
      return [Truck, Clock, Building, Ship][index - 1] || Truck;
    } else if (roleUpper === 'SUPPLIER') {
      return [FileText, FileText, ShoppingCart, DollarSign][index - 1] || FileText;
    } else {
      return [ShoppingBag, ShoppingBag, MapPin, HelpCircle][index - 1] || ShoppingBag;
    }
  };

  const pageTitle = summary?.role_title || (
    roleUpper === 'ADMIN' ? 'Admin Home' :
    (roleUpper === 'LOGISTICS_MANAGER' || roleUpper === 'SUPPLY_CHAIN_ANALYST') ? 'Shipping Home' :
    roleUpper === 'SUPPLIER' ? 'Supplier Home' :
    roleUpper === 'CUSTOMER' ? 'My Orders Home' : 'Buying Home'
  );

  const pageHelpText = (
    roleUpper === 'ADMIN' ? 'Central dashboard for administrators to monitor platform users, suppliers, and system operations.' :
    (roleUpper === 'LOGISTICS_MANAGER' || roleUpper === 'SUPPLY_CHAIN_ANALYST') ? 'Operations hub for tracking shipments, delivery routes, warehouses, and freight carriers.' :
    roleUpper === 'SUPPLIER' ? 'Self-service vendor console to respond to buyer price requests and manage order fulfillment.' :
    roleUpper === 'CUSTOMER' ? 'Client portal for placing and tracking your orders and contacting customer support.' :
    'Procurement console for managing supplier requests, automated price talks, and purchase orders.'
  );

  const cardsData = [
    summary?.card1 || { label: 'Card 1', value: '...', change: '' },
    summary?.card2 || { label: 'Card 2', value: '...', change: '' },
    summary?.card3 || { label: 'Card 3', value: '...', change: '' },
    summary?.card4 || { label: 'Card 4', value: '...', change: '' },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* ── Top Page Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-xl bg-white border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">{pageTitle}</h1>
            <HelpTooltip text={pageHelpText} />
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Welcome back, <span className="font-semibold text-slate-800">{user?.full_name || 'User'}</span> ({user?.role_display || role})
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={loading}
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold text-slate-700 bg-slate-50 hover:bg-slate-100 border border-slate-200 transition-colors shrink-0"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-[#8e3a59]' : ''}`} />
          Refresh
        </button>
      </div>

      {/* ── 4 Clickable Summary Cards ── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {cardsData.map((c, i) => {
          const Icon = getCardIcon(i + 1);
          return (
            <div
              key={i}
              onClick={() => handleCardClick(i + 1)}
              className="p-5 rounded-xl bg-white border border-slate-200 hover:border-[#8e3a59]/40 hover:shadow-md transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{c.label}</span>
                <div className="w-8 h-8 rounded-lg bg-slate-50 group-hover:bg-[#8e3a59]/10 text-slate-600 group-hover:text-[#8e3a59] flex items-center justify-center transition-colors">
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div className="flex items-baseline justify-between">
                <p className="text-2xl font-extrabold text-slate-900 tracking-tight">{c.value}</p>
                <ArrowRight className="w-4 h-4 text-slate-300 group-hover:text-[#8e3a59] group-hover:translate-x-1 transition-all" />
              </div>
              {c.change && (
                <p className="text-[11px] text-slate-500 mt-1 font-medium">{c.change}</p>
              )}
            </div>
          );
        })}
      </div>

      {/* ── AI Assistant Card (Not shown to Customer) ── */}
      {roleUpper !== 'CUSTOMER' && (
        <AIAssistantCard
          role={roleUpper}
          onActionNotice={(msg) => setToastMessage(msg)}
        />
      )}

      {/* ── Recent Activity List (5 Items) ── */}
      <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div>
            <h2 className="text-base font-bold text-slate-900 tracking-tight">Recent Activity</h2>
            <p className="text-xs text-slate-500">Latest platform actions and operational updates</p>
          </div>
          {roleUpper === 'ADMIN' && (
            <button
              onClick={() => setCurrentPage('audit_logs')}
              className="text-xs font-semibold text-[#8e3a59] hover:underline"
            >
              View Full History &rarr;
            </button>
          )}
        </div>

        {activityLogs.length === 0 ? (
          <p className="text-xs text-slate-400 py-4 text-center">No recent activity recorded yet.</p>
        ) : (
          <div className="divide-y divide-slate-100">
            {activityLogs.map((log) => (
              <div key={log.id} className="py-3 flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center shrink-0 text-slate-600">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-slate-900">{log.item}</p>
                    <p className="text-[11px] text-slate-500">
                      By <span className="font-semibold text-slate-700">{log.user}</span> &bull; {log.date}
                    </p>
                  </div>
                </div>
                <StatusBadge status={log.action === 'CREATE' ? 'APPROVED' : (log.action === 'DELETE' ? 'CANCELLED' : 'IN_PROGRESS')} />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Toast Notification */}
      {toastMessage && (
        <Toast
          message={toastMessage}
          onClose={() => setToastMessage('')}
        />
      )}
    </div>
  );
};
