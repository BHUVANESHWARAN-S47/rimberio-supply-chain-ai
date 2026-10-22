import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { RimberioAPI } from '../services/api';
import { formatINR } from '../utils/currency';
import {
  Building2,
  Package,
  TrendingUp,
  RefreshCw,
  Plus,
  X,
  CheckCircle2,
  FileText,
  FileCheck,
  ShoppingCart,
  MessageSquare,
  Sparkles,
  AlertTriangle,
  Clock,
  Edit2,
  Trash2,
  Award,
  Send,
} from 'lucide-react';
import {
  HelpTooltip,
  StatusBadge,
  DeleteConfirmDialog,
  EmptyState,
  Toast,
} from '../components/common/CommonUI';

export const SupplierPortalPage = ({ initialTab = 'company' }) => {
  const { user, setCurrentPage } = useApp();
  const [activeTab, setActiveTab] = useState(initialTab);
  const [loading, setLoading] = useState(true);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');

  // Company Profile
  const [profile, setProfile] = useState({
    name: 'Apex Precision Systems Ltd',
    country: 'Bengaluru / Karnataka, India',
    contact: 'sales@apexprecision.in',
    phone: '+91 80 4123 9800',
    certificates: 'ISO-9001:2015, AS9100D Aerospace Certified',
  });
  const [showEditProfileModal, setShowEditProfileModal] = useState(false);

  // Products
  const [products, setProducts] = useState([]);
  const [showProductModal, setShowProductModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [productForm, setProductForm] = useState({
    name: '',
    sku: '',
    unit_cost: 140,
    min_order_qty: 500,
    delivery_days: 10,
    stock_available: 5000,
  });

  // Price Requests (RFQs) & Quotes
  const [rfqs, setRfqs] = useState([]);
  const [quotes, setQuotes] = useState([]);
  const [showQuoteModal, setShowQuoteModal] = useState(false);
  const [quoteTargetRfq, setQuoteTargetRfq] = useState(null);
  const [quoteForm, setQuoteForm] = useState({
    price: 145,
    quantity: 1000,
    delivery_days: 10,
  });

  // Orders To Deliver (POs)
  const [ordersToDeliver, setOrdersToDeliver] = useState([]);

  // Delete State
  const [deleteDialog, setDeleteDialog] = useState({
    isOpen: false,
    itemType: '',
    item: null,
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const [prodRes, rfqRes, quoteRes, poRes] = await Promise.all([
        RimberioAPI.getProducts().catch(() => []),
        RimberioAPI.getRFQs().catch(() => []),
        RimberioAPI.getQuotes().catch(() => []),
        RimberioAPI.getPurchaseOrders().catch(() => []),
      ]);

      setProducts(Array.isArray(prodRes) ? prodRes : []);
      setRfqs(Array.isArray(rfqRes) ? rfqRes : []);
      setQuotes(Array.isArray(quoteRes) ? quoteRes : []);
      setOrdersToDeliver(Array.isArray(poRes) ? poRes : []);
    } catch (err) {
      setToastMessage('Error loading supplier portal data');
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

  // Profile Update
  const handleSaveProfile = (e) => {
    e.preventDefault();
    setShowEditProfileModal(false);
    setToastMessage('Company profile updated successfully.');
    setToastType('success');
  };

  // Product CRUD
  const handleOpenAddProduct = () => {
    setEditingProduct(null);
    setProductForm({
      name: '',
      sku: `PRD-${Math.floor(1000 + Math.random() * 9000)}`,
      unit_cost: 140,
      min_order_qty: 500,
      delivery_days: 10,
      stock_available: 5000,
    });
    setShowProductModal(true);
  };

  const handleOpenEditProduct = (p) => {
    setEditingProduct(p);
    setProductForm({
      name: p.name || '',
      sku: p.sku || '',
      unit_cost: p.unit_cost || 140,
      min_order_qty: p.min_order_qty || 500,
      delivery_days: p.lead_time_days || 10,
      stock_available: p.stock_available || 5000,
    });
    setShowProductModal(true);
  };

  const handleSaveProduct = async (e) => {
    e.preventDefault();
    try {
      if (editingProduct) {
        await RimberioAPI.updateProduct(editingProduct.id, {
          name: productForm.name,
          sku: productForm.sku,
          unit_cost: parseFloat(productForm.unit_cost),
          selling_price: parseFloat(productForm.unit_cost) * 1.25,
        });
        setToastMessage(`Product "${productForm.name}" updated.`);
      } else {
        await RimberioAPI.createProduct({
          name: productForm.name,
          sku: productForm.sku,
          unit_cost: parseFloat(productForm.unit_cost),
          selling_price: parseFloat(productForm.unit_cost) * 1.25,
          category: 'Micro-Components',
        });
        setToastMessage(`Product "${productForm.name}" registered.`);
      }
      setToastType('success');
      setShowProductModal(false);
      loadData();
    } catch (err) {
      setToastMessage(err.message || 'Product save failed');
      setToastType('error');
    }
  };

  // Send Quote
  const handleSendQuote = async (e) => {
    e.preventDefault();
    if (!quoteTargetRfq) return;
    try {
      await RimberioAPI.createQuote({
        rfq_id: quoteTargetRfq.id || quoteTargetRfq.rfq_number,
        supplier_id: user?.email || 'Apex Precision',
        price: parseFloat(quoteForm.price),
        quantity: parseInt(quoteForm.quantity, 10),
        delivery_days: parseInt(quoteForm.delivery_days, 10),
        status: 'SUBMITTED',
      });
      setToastMessage(`Quote sent for Price Request #${quoteTargetRfq.rfq_number || quoteTargetRfq.id}.`);
      setToastType('success');
      setShowQuoteModal(false);
      loadData();
    } catch (err) {
      setToastMessage(err.message || 'Failed to submit quote');
      setToastType('error');
    }
  };

  const handleWithdrawQuote = async (quote) => {
    try {
      await RimberioAPI.deleteQuote(quote.id);
      setToastMessage('Quote withdrawn.');
      setToastType('success');
      loadData();
    } catch (err) {
      setToastMessage(err.message || 'Failed to withdraw quote');
      setToastType('error');
    }
  };

  // Order Fulfillment Status Buttons
  const handleUpdateOrderStatus = async (po, newStatus) => {
    try {
      await RimberioAPI.updatePOStatus(po.id, newStatus);
      setToastMessage(`Order ${po.po_number} marked as ${newStatus}.`);
      setToastType('success');
      loadData();
    } catch (err) {
      setToastMessage(err.message || 'Status update failed');
      setToastType('error');
    }
  };

  const confirmDelete = async () => {
    if (!deleteDialog.item) return;
    try {
      if (deleteDialog.itemType === 'product') {
        await RimberioAPI.deleteProduct(deleteDialog.item.id);
        setToastMessage('Product deleted.');
      }
      setToastType('success');
      setDeleteDialog({ isOpen: false, itemType: '', item: null });
      loadData();
    } catch (err) {
      setToastMessage(err.message || 'Delete failed');
      setToastType('error');
    }
  };

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-xl bg-white border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider bg-[#8e3a59]/10 text-[#8e3a59]">
              <Building2 className="w-3.5 h-3.5" />
              Supplier Portal
            </span>
          </div>
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              {activeTab === 'company'
                ? 'My Company'
                : activeTab === 'products'
                ? 'My Products'
                : activeTab === 'rfqs'
                ? 'Price Requests & Quotes'
                : activeTab === 'talks'
                ? 'Price Talks'
                : 'Orders To Deliver'}
            </h1>
            <HelpTooltip text="Manage catalog offerings, quote on buyer price requests, and confirm orders to deliver." />
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Supplier Operations Center · {profile.name}
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
          {activeTab === 'products' && (
            <button
              onClick={handleOpenAddProduct}
              className="px-4 py-2 rounded-lg bg-[#8e3a59] hover:bg-[#782f49] text-white text-xs font-bold shadow-sm flex items-center gap-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              + Add Product
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2 overflow-x-auto">
        {[
          { id: 'company', label: 'My Company', icon: Building2 },
          { id: 'products', label: `My Products (${products.length})`, icon: Package },
          { id: 'rfqs', label: `Price Requests & Quotes (${rfqs.length})`, icon: FileText },
          { id: 'talks', label: 'Price Talks', icon: MessageSquare },
          { id: 'orders', label: `Orders To Deliver (${ordersToDeliver.length})`, icon: ShoppingCart },
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
          <span className="text-xs text-slate-500 font-medium">New Price Requests</span>
          <div className="text-2xl font-bold text-slate-900 mt-1">{rfqs.length}</div>
          <p className="text-[11px] text-slate-400 mt-0.5">Buyer opportunities</p>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Quotes Sent</span>
          <div className="text-2xl font-bold text-blue-700 mt-1">{quotes.length}</div>
          <p className="text-[11px] text-slate-400 mt-0.5">Active bids submitted</p>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Orders To Deliver</span>
          <div className="text-2xl font-bold text-emerald-700 mt-1">{ordersToDeliver.length}</div>
          <p className="text-[11px] text-slate-400 mt-0.5">Confirmed purchase commitments</p>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Payments Pending</span>
          <div className="text-2xl font-bold text-[#8e3a59] mt-1">₹4,85,000</div>
          <p className="text-[11px] text-slate-400 mt-0.5">Pending invoicing</p>
        </div>
      </div>

      {/* Supplier AI Assistant Card */}
      <div className="p-4 rounded-xl bg-gradient-to-r from-[#8e3a59]/10 via-[#8e3a59]/5 to-transparent border border-[#8e3a59]/20 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-[#8e3a59] text-white flex items-center justify-center shrink-0">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#8e3a59]">Supplier AI Assistant</span>
            <p className="text-xs font-semibold text-slate-800 mt-0.5">
              Offer 4% discount for 2,500+ units to win more enterprise orders from Tata Advanced Systems.
            </p>
          </div>
        </div>

        <button
          onClick={() => {
            setToastMessage('Discount strategy applied to catalog tiers.');
            setToastType('success');
          }}
          className="px-4 py-2 rounded-lg bg-[#8e3a59] hover:bg-[#782f49] text-white text-xs font-bold shadow-sm whitespace-nowrap"
        >
          Apply Discount
        </button>
      </div>

      {/* ── TAB 1: MY COMPANY ── */}
      {activeTab === 'company' && (
        <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-sm space-y-6">
          <div className="flex items-center justify-between border-b border-slate-100 pb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">Company Profile</h3>
              <p className="text-xs text-slate-500">Corporate credentials, manufacturing location, and industry certifications</p>
            </div>
            <button
              onClick={() => setShowEditProfileModal(true)}
              className="px-3.5 py-1.5 rounded-lg border border-slate-300 text-xs font-semibold text-slate-700 hover:bg-slate-50 flex items-center gap-1.5"
            >
              <Edit2 className="w-3.5 h-3.5" />
              Edit Profile
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
            <div className="space-y-4">
              <div>
                <span className="text-slate-400 font-medium block">Company Name:</span>
                <span className="text-sm font-bold text-slate-900 mt-0.5 block">{profile.name}</span>
              </div>
              <div>
                <span className="text-slate-400 font-medium block">Manufacturing Hub & Country:</span>
                <span className="font-semibold text-slate-800 mt-0.5 block">{profile.country}</span>
              </div>
              <div>
                <span className="text-slate-400 font-medium block">Contact Email:</span>
                <span className="font-mono text-slate-800 mt-0.5 block">{profile.contact}</span>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <span className="text-slate-400 font-medium block">Direct Phone:</span>
                <span className="font-mono text-slate-800 mt-0.5 block">{profile.phone}</span>
              </div>
              <div>
                <span className="text-slate-400 font-medium block">Quality Certificates:</span>
                <div className="flex items-center gap-2 mt-1">
                  <Award className="w-4 h-4 text-emerald-600" />
                  <span className="font-semibold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                    {profile.certificates}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── TAB 2: MY PRODUCTS ── */}
      {activeTab === 'products' && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 font-bold uppercase text-[11px] border-b border-slate-200">
                <tr>
                  <th className="px-5 py-3.5">Product</th>
                  <th className="px-5 py-3.5">Product Code</th>
                  <th className="px-5 py-3.5">Price / Unit</th>
                  <th className="px-5 py-3.5">Min Order</th>
                  <th className="px-5 py-3.5">Delivery Days</th>
                  <th className="px-5 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {products.map((p) => (
                  <tr key={p.id || p.sku} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-5 py-3.5 font-semibold text-slate-900">{p.name}</td>
                    <td className="px-5 py-3.5 font-mono text-slate-600">{p.sku}</td>
                    <td className="px-5 py-3.5 font-mono font-bold text-slate-900">
                      {formatINR(p.unit_cost || 140, 2)}
                    </td>
                    <td className="px-5 py-3.5 text-slate-700">500 units</td>
                    <td className="px-5 py-3.5 text-slate-700 font-medium">10 days</td>
                    <td className="px-5 py-3.5 text-right space-x-2">
                      <button
                        onClick={() => handleOpenEditProduct(p)}
                        className="px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded border border-slate-200"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => setDeleteDialog({ isOpen: true, itemType: 'product', item: p })}
                        className="px-2.5 py-1 text-xs font-semibold text-rose-600 hover:bg-rose-50 rounded border border-rose-200"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {products.length === 0 && !loading && (
            <div className="p-8">
              <EmptyState message="No products in catalog." actionLabel="+ Add first product" onAction={handleOpenAddProduct} />
            </div>
          )}
        </div>
      )}

      {/* ── TAB 3: PRICE REQUESTS & QUOTES ── */}
      {activeTab === 'rfqs' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-100">
              <h3 className="text-sm font-bold text-slate-900">Buyer Price Requests (RFQs)</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 font-bold uppercase text-[11px] border-b border-slate-200">
                  <tr>
                    <th className="px-5 py-3.5">Request No.</th>
                    <th className="px-5 py-3.5">Quantity</th>
                    <th className="px-5 py-3.5">Needed By</th>
                    <th className="px-5 py-3.5">Status</th>
                    <th className="px-5 py-3.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {rfqs.map((rfq) => (
                    <tr key={rfq.id} className="hover:bg-slate-50/60 transition-colors">
                      <td className="px-5 py-3.5 font-mono font-bold text-slate-900">
                        {rfq.rfq_number || `RFQ-${rfq.id}`}
                      </td>
                      <td className="px-5 py-3.5 font-mono text-slate-700">
                        {(rfq.quantity || 1000).toLocaleString()} units
                      </td>
                      <td className="px-5 py-3.5 text-slate-600">{rfq.needed_by || 'Flexible'}</td>
                      <td className="px-5 py-3.5">
                        <StatusBadge status={rfq.status} />
                      </td>
                      <td className="px-5 py-3.5 text-right">
                        <button
                          onClick={() => {
                            setQuoteTargetRfq(rfq);
                            setQuoteForm({ price: 140, quantity: rfq.quantity || 1000, delivery_days: 10 });
                            setShowQuoteModal(true);
                          }}
                          className="px-3 py-1.5 rounded-lg bg-[#8e3a59] hover:bg-[#782f49] text-white text-xs font-bold shadow-sm"
                        >
                          Send Quote
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Submitted Quotes */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-100">
              <h3 className="text-sm font-bold text-slate-900">My Submitted Quotes</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 font-bold uppercase text-[11px] border-b border-slate-200">
                  <tr>
                    <th className="px-5 py-3.5">Request No.</th>
                    <th className="px-5 py-3.5">Quoted Price</th>
                    <th className="px-5 py-3.5">Quantity</th>
                    <th className="px-5 py-3.5">Delivery Days</th>
                    <th className="px-5 py-3.5">Status</th>
                    <th className="px-5 py-3.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {quotes.map((q) => (
                    <tr key={q.id} className="hover:bg-slate-50/60 transition-colors">
                      <td className="px-5 py-3.5 font-mono font-bold text-slate-900">{q.rfq_id}</td>
                      <td className="px-5 py-3.5 font-mono font-bold text-slate-900">{formatINR(q.price, 2)}</td>
                      <td className="px-5 py-3.5 font-mono text-slate-700">{(q.quantity || 1000).toLocaleString()}</td>
                      <td className="px-5 py-3.5 text-slate-700">{q.delivery_days || 10} days</td>
                      <td className="px-5 py-3.5"><StatusBadge status={q.status} /></td>
                      <td className="px-5 py-3.5 text-right">
                        <button
                          onClick={() => handleWithdrawQuote(q)}
                          className="px-2.5 py-1 text-xs font-semibold text-rose-600 hover:bg-rose-50 rounded border border-rose-200"
                        >
                          Withdraw
                        </button>
                      </td>
                    </tr>
                  ))}
                  {quotes.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-5 py-6 text-center text-slate-500">
                        No quotes submitted yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ── TAB 4: PRICE TALKS ── */}
      {activeTab === 'talks' && (
        <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="text-base font-bold text-slate-900">Active Price Talks with Buyer</h3>
              <p className="text-xs text-slate-500">Review buyer bids and counter or accept commercial terms</p>
            </div>
            <button
              onClick={() => setCurrentPage('negotiation')}
              className="px-4 py-2 rounded-lg bg-[#8e3a59] text-white text-xs font-bold hover:bg-[#782f49] shadow-sm flex items-center gap-1.5"
            >
              Open Full Price Talk Console
            </button>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-3">
            <div className="flex justify-between items-center">
              <div>
                <span className="text-[10px] text-slate-400 font-bold uppercase">Latest Buyer Offer</span>
                <p className="text-base font-bold text-slate-900 mt-0.5 font-mono">₹148.20 / unit</p>
                <p className="text-slate-500 text-[11px]">Requested Lead Time: 12 days</p>
              </div>
              <StatusBadge status="ACTIVE" />
            </div>

            <div className="flex items-center gap-2 pt-2 border-t border-slate-200">
              <button
                onClick={() => {
                  setToastMessage('Buyer offer accepted. Purchase order will be released.');
                  setToastType('success');
                }}
                className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-sm"
              >
                Accept
              </button>
              <button
                onClick={() => setCurrentPage('negotiation')}
                className="px-4 py-2 rounded-lg bg-[#8e3a59] hover:bg-[#782f49] text-white text-xs font-bold shadow-sm"
              >
                Counter Offer
              </button>
              <button
                onClick={() => {
                  setToastMessage('Buyer offer declined.');
                  setToastType('info');
                }}
                className="px-3.5 py-2 rounded-lg border border-rose-200 text-rose-700 hover:bg-rose-50 text-xs font-semibold"
              >
                Decline
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── TAB 5: ORDERS TO DELIVER ── */}
      {activeTab === 'orders' && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 font-bold uppercase text-[11px] border-b border-slate-200">
                <tr>
                  <th className="px-5 py-3.5">PO Number</th>
                  <th className="px-5 py-3.5">Total Amount</th>
                  <th className="px-5 py-3.5">Order Date</th>
                  <th className="px-5 py-3.5">Status</th>
                  <th className="px-5 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {ordersToDeliver.map((po) => (
                  <tr key={po.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-5 py-3.5 font-mono font-bold text-slate-900">{po.po_number}</td>
                    <td className="px-5 py-3.5 font-mono font-bold text-slate-900">{formatINR(po.total_amount, 2)}</td>
                    <td className="px-5 py-3.5 text-slate-600">{po.order_date || 'Recent'}</td>
                    <td className="px-5 py-3.5"><StatusBadge status={po.status} /></td>
                    <td className="px-5 py-3.5 text-right space-x-1.5">
                      <button
                        onClick={() => handleUpdateOrderStatus(po, 'APPROVED')}
                        className="px-2.5 py-1 text-xs font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 rounded border border-emerald-200"
                      >
                        Confirm Order
                      </button>
                      <button
                        onClick={() => handleUpdateOrderStatus(po, 'SHIPPED')}
                        className="px-2.5 py-1 text-xs font-bold text-blue-700 bg-blue-50 hover:bg-blue-100 rounded border border-blue-200"
                      >
                        Mark Shipped
                      </button>
                      <button
                        onClick={() => {
                          setToastMessage(`Issue flagged on order ${po.po_number}. Logistics notified.`);
                          setToastType('info');
                        }}
                        className="px-2.5 py-1 text-xs font-semibold text-rose-700 hover:bg-rose-50 rounded border border-rose-200"
                      >
                        Report Problem
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {ordersToDeliver.length === 0 && !loading && (
            <div className="p-8">
              <EmptyState message="No active purchase orders to deliver." />
            </div>
          )}
        </div>
      )}

      {/* Edit Profile Modal */}
      {showEditProfileModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="w-full max-w-md bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">Edit Company Profile</h3>
              <button onClick={() => setShowEditProfileModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSaveProfile} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Company Name</label>
                <input
                  type="text"
                  value={profile.name}
                  onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Country / Hub</label>
                <input
                  type="text"
                  value={profile.country}
                  onChange={(e) => setProfile({ ...profile, country: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Contact Email</label>
                <input
                  type="email"
                  value={profile.contact}
                  onChange={(e) => setProfile({ ...profile, contact: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Certificates</label>
                <input
                  type="text"
                  value={profile.certificates}
                  onChange={(e) => setProfile({ ...profile, certificates: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowEditProfileModal(false)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-100 border border-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-[#8e3a59] hover:bg-[#782f49] shadow-sm"
                >
                  Save Profile
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add / Edit Product Modal */}
      {showProductModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="w-full max-w-md bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">
                {editingProduct ? 'Edit Product' : '+ Add Product'}
              </h3>
              <button onClick={() => setShowProductModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSaveProduct} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Product Name</label>
                <input
                  type="text"
                  value={productForm.name}
                  onChange={(e) => setProductForm({ ...productForm, name: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Product Code</label>
                <input
                  type="text"
                  value={productForm.sku}
                  onChange={(e) => setProductForm({ ...productForm, sku: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Price per unit (₹)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={productForm.unit_cost}
                    onChange={(e) => setProductForm({ ...productForm, unit_cost: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Delivery Days</label>
                  <input
                    type="number"
                    value={productForm.delivery_days}
                    onChange={(e) => setProductForm({ ...productForm, delivery_days: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowProductModal(false)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-100 border border-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-[#8e3a59] hover:bg-[#782f49] shadow-sm"
                >
                  Save Product
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Send Quote Modal */}
      {showQuoteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="w-full max-w-md bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">Send Price Quote</h3>
              <button onClick={() => setShowQuoteModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSendQuote} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Quoted Price per unit (₹)</label>
                <input
                  type="number"
                  step="0.01"
                  value={quoteForm.price}
                  onChange={(e) => setQuoteForm({ ...quoteForm, price: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Quantity Available</label>
                <input
                  type="number"
                  value={quoteForm.quantity}
                  onChange={(e) => setQuoteForm({ ...quoteForm, quantity: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Delivery Days</label>
                <input
                  type="number"
                  value={quoteForm.delivery_days}
                  onChange={(e) => setQuoteForm({ ...quoteForm, delivery_days: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowQuoteModal(false)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-100 border border-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-[#8e3a59] hover:bg-[#782f49] shadow-sm"
                >
                  Submit Quote
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Dialog */}
      <DeleteConfirmDialog
        isOpen={deleteDialog.isOpen}
        itemName={deleteDialog.item?.name || 'this item'}
        onConfirm={confirmDelete}
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
