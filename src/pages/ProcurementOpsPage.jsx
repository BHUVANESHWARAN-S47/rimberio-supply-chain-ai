import React, { useState, useEffect } from 'react';
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
import {
  ShoppingCart,
  FileText,
  FileCheck,
  Plus,
  RefreshCw,
  Search,
  CheckCircle,
  XCircle,
  Edit2,
  Trash2,
  X,
  ArrowRight,
  Clock,
  Building2,
} from 'lucide-react';

export const ProcurementOpsPage = ({ initialTab = 'rfqs' }) => {
  const { setCurrentPage } = useApp();
  const [activeTab, setActiveTab] = useState(initialTab === 'orders' ? 'orders' : 'rfqs');
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Data
  const [rfqs, setRfqs] = useState([]);
  const [quotes, setQuotes] = useState([]);
  const [purchaseOrders, setPurchaseOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [suppliers, setSuppliers] = useState([]);

  // Toast
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');

  // RFQ Modal State
  const [showRfqModal, setShowRfqModal] = useState(false);
  const [editingRfq, setEditingRfq] = useState(null);
  const [rfqForm, setRfqForm] = useState({
    product_id: '',
    quantity: 1000,
    needed_by: new Date(Date.now() + 14 * 86400000).toISOString().split('T')[0],
  });

  // PO Modal State
  const [showPoModal, setShowPoModal] = useState(false);
  const [editingPo, setEditingPo] = useState(null);
  const [poForm, setPoForm] = useState({
    po_number: '',
    supplier_id: '',
    total_amount: 150000,
    status: 'DRAFT',
  });

  // Delete Dialog
  const [deleteDialog, setDeleteDialog] = useState({
    isOpen: false,
    itemType: '',
    item: null,
  });

  // Selected RFQ for viewing quotes
  const [selectedRfqForQuotes, setSelectedRfqForQuotes] = useState(null);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [rRes, qRes, pRes, prodRes, suppRes] = await Promise.all([
        RimberioAPI.getRFQs().catch(() => []),
        RimberioAPI.getQuotes().catch(() => []),
        RimberioAPI.getPurchaseOrders().catch(() => []),
        RimberioAPI.getProducts().catch(() => []),
        RimberioAPI.getSuppliers().catch(() => []),
      ]);
      setRfqs(Array.isArray(rRes) ? rRes : []);
      setQuotes(Array.isArray(qRes) ? qRes : []);
      setPurchaseOrders(Array.isArray(pRes) ? pRes : []);
      setProducts(Array.isArray(prodRes) ? prodRes : []);
      setSuppliers(Array.isArray(suppRes) ? suppRes : []);
    } catch (err) {
      setToastMessage('Error loading procurement data');
      setToastType('error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  useEffect(() => {
    if (initialTab === 'orders' || initialTab === 'rfqs') {
      setActiveTab(initialTab);
    }
  }, [initialTab]);

  // Handle New / Edit RFQ
  const handleOpenAddRfq = () => {
    setEditingRfq(null);
    setRfqForm({
      product_id: products[0]?.id || 'PRD-1',
      quantity: 1000,
      needed_by: new Date(Date.now() + 14 * 86400000).toISOString().split('T')[0],
    });
    setShowRfqModal(true);
  };

  const handleOpenEditRfq = (rfq) => {
    setEditingRfq(rfq);
    setRfqForm({
      product_id: rfq.product_id || '',
      quantity: rfq.quantity || 1000,
      needed_by: rfq.needed_by || '',
    });
    setShowRfqModal(true);
  };

  const handleSaveRfq = async (e) => {
    e.preventDefault();
    try {
      if (editingRfq) {
        await RimberioAPI.updateRFQ(editingRfq.id, {
          product_id: rfqForm.product_id,
          quantity: parseInt(rfqForm.quantity, 10),
          needed_by: rfqForm.needed_by,
        });
        setToastMessage('Price Request updated successfully.');
      } else {
        await RimberioAPI.createRFQ({
          product_id: rfqForm.product_id,
          quantity: parseInt(rfqForm.quantity, 10),
          needed_by: rfqForm.needed_by,
          status: 'PENDING',
        });
        setToastMessage('Price Request created successfully.');
      }
      setToastType('success');
      setShowRfqModal(false);
      loadAll();
    } catch (err) {
      setToastMessage(err.message || 'Operation failed');
      setToastType('error');
    }
  };

  const handleCancelRfq = async (rfq) => {
    try {
      await RimberioAPI.updateRFQ(rfq.id, { status: 'CANCELLED' });
      setToastMessage(`Price Request #${rfq.rfq_number || rfq.id} cancelled.`);
      setToastType('success');
      loadAll();
    } catch (err) {
      setToastMessage(err.message || 'Failed to cancel');
      setToastType('error');
    }
  };

  // Quotes Action
  const handleAcceptQuote = async (quote) => {
    try {
      await RimberioAPI.updateQuote(quote.id, { status: 'ACCEPTED' });

      // Automatically create a Purchase Order from accepted deal
      const poNum = `PO-${Math.floor(10000 + Math.random() * 90000)}`;
      await RimberioAPI.createPurchaseOrder({
        po_number: poNum,
        supplier_id: quote.supplier_id || 'SUP-1',
        total_amount: Number(quote.price || 150) * Number(quote.quantity || 1000),
        status: 'APPROVED',
      });

      setToastMessage(`Quote accepted! Purchase Order ${poNum} created.`);
      setToastType('success');
      loadAll();
    } catch (err) {
      setToastMessage(err.message || 'Failed to accept quote');
      setToastType('error');
    }
  };

  const handleRejectQuote = async (quote) => {
    try {
      await RimberioAPI.updateQuote(quote.id, { status: 'REJECTED' });
      setToastMessage('Quote rejected.');
      setToastType('success');
      loadAll();
    } catch (err) {
      setToastMessage(err.message || 'Failed to reject quote');
      setToastType('error');
    }
  };

  // Handle POs
  const handleOpenAddPo = () => {
    setEditingPo(null);
    setPoForm({
      po_number: `PO-${Math.floor(10000 + Math.random() * 90000)}`,
      supplier_id: suppliers[0]?.code || 'SUP-001',
      total_amount: 150000,
      status: 'DRAFT',
    });
    setShowPoModal(true);
  };

  const handleOpenEditPo = (po) => {
    setEditingPo(po);
    setPoForm({
      po_number: po.po_number || '',
      supplier_id: po.supplier_id || '',
      total_amount: po.total_amount || 0,
      status: po.status || 'DRAFT',
    });
    setShowPoModal(true);
  };

  const handleSavePo = async (e) => {
    e.preventDefault();
    try {
      if (editingPo) {
        await RimberioAPI.updatePurchaseOrder(editingPo.id, {
          total_amount: parseFloat(poForm.total_amount),
          status: poForm.status,
        });
        setToastMessage(`Purchase Order ${editingPo.po_number} updated.`);
      } else {
        await RimberioAPI.createPurchaseOrder({
          po_number: poForm.po_number,
          supplier_id: poForm.supplier_id,
          total_amount: parseFloat(poForm.total_amount),
          status: poForm.status,
        });
        setToastMessage(`Purchase Order ${poForm.po_number} created.`);
      }
      setToastType('success');
      setShowPoModal(false);
      loadAll();
    } catch (err) {
      setToastMessage(err.message || 'Operation failed');
      setToastType('error');
    }
  };

  const handleApprovePo = async (po) => {
    try {
      await RimberioAPI.updatePurchaseOrder(po.id, { status: 'APPROVED' });
      setToastMessage(`Purchase Order ${po.po_number} approved.`);
      setToastType('success');
      loadAll();
    } catch (err) {
      setToastMessage(err.message || 'Approval failed');
      setToastType('error');
    }
  };

  const handleCancelPo = async (po) => {
    try {
      await RimberioAPI.updatePurchaseOrder(po.id, { status: 'CANCELLED' });
      setToastMessage(`Purchase Order ${po.po_number} cancelled.`);
      setToastType('success');
      loadAll();
    } catch (err) {
      setToastMessage(err.message || 'Cancel failed');
      setToastType('error');
    }
  };

  const confirmDelete = async () => {
    if (!deleteDialog.item) return;
    try {
      if (deleteDialog.itemType === 'rfq') {
        await RimberioAPI.deleteRFQ(deleteDialog.item.id);
        setToastMessage(`Price Request deleted.`);
      } else if (deleteDialog.itemType === 'po') {
        await RimberioAPI.deletePurchaseOrder(deleteDialog.item.id);
        setToastMessage(`Purchase Order deleted.`);
      }
      setToastType('success');
      setDeleteDialog({ isOpen: false, itemType: '', item: null });
      loadAll();
    } catch (err) {
      setToastMessage(err.message || 'Delete failed');
      setToastType('error');
    }
  };

  // Find productName helper
  const getProductName = (id) => {
    const p = products.find((prod) => prod.id === id || prod.sku === id);
    return p ? `${p.name} (${p.sku})` : id || 'Item';
  };

  const getSupplierName = (id) => {
    const s = suppliers.find((sup) => sup.id === id || sup.code === id);
    return s ? s.name : id || 'Supplier';
  };

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-xl bg-white border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider bg-[#8e3a59]/10 text-[#8e3a59]">
              <ShoppingCart className="w-3.5 h-3.5" />
              Buying & Orders
            </span>
          </div>
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              {activeTab === 'rfqs' ? 'Price Requests' : 'Purchase Orders'}
            </h1>
            <HelpTooltip text="Request supplier price bids, review quotes, and issue binding purchase orders." />
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            {activeTab === 'rfqs'
              ? 'Send price requests to suppliers, receive quotes, and accept competitive offers.'
              : 'Track approved purchase commitments and release confirmed orders.'}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadAll}
            disabled={loading}
            className="px-3.5 py-2 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 transition-colors flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          {activeTab === 'rfqs' ? (
            <button
              onClick={handleOpenAddRfq}
              className="px-4 py-2 rounded-lg bg-[#8e3a59] hover:bg-[#782f49] text-white text-xs font-bold shadow-sm transition-colors flex items-center gap-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              + New Request
            </button>
          ) : (
            <button
              onClick={handleOpenAddPo}
              className="px-4 py-2 rounded-lg bg-[#8e3a59] hover:bg-[#782f49] text-white text-xs font-bold shadow-sm transition-colors flex items-center gap-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              + New Purchase Order
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => setActiveTab('rfqs')}
          className={`px-4 py-2 rounded-lg text-xs font-bold flex items-center gap-2 transition-all ${
            activeTab === 'rfqs'
              ? 'bg-[#8e3a59] text-white shadow-sm'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <FileText className="w-4 h-4" />
          Price Requests ({rfqs.length})
        </button>
        <button
          onClick={() => setActiveTab('orders')}
          className={`px-4 py-2 rounded-lg text-xs font-bold flex items-center gap-2 transition-all ${
            activeTab === 'orders'
              ? 'bg-[#8e3a59] text-white shadow-sm'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <ShoppingCart className="w-4 h-4" />
          Purchase Orders ({purchaseOrders.length})
        </button>
      </div>

      {/* 4 Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Open Price Requests</span>
          <div className="text-2xl font-bold text-slate-900 mt-1">
            {rfqs.filter((r) => r.status === 'PENDING' || r.status === 'ACTIVE').length}
          </div>
          <p className="text-[11px] text-slate-400 mt-0.5">Awaiting supplier replies</p>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Supplier Quotes Received</span>
          <div className="text-2xl font-bold text-blue-700 mt-1">{quotes.length}</div>
          <p className="text-[11px] text-slate-400 mt-0.5">Available for review</p>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Orders Waiting Approval</span>
          <div className="text-2xl font-bold text-amber-700 mt-1">
            {purchaseOrders.filter((po) => po.status === 'DRAFT' || po.status === 'PENDING').length}
          </div>
          <p className="text-[11px] text-slate-400 mt-0.5">Draft commitments</p>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Approved Orders</span>
          <div className="text-2xl font-bold text-emerald-700 mt-1">
            {purchaseOrders.filter((po) => po.status === 'APPROVED' || po.status === 'COMPLETED').length}
          </div>
          <p className="text-[11px] text-slate-400 mt-0.5">In fulfillment</p>
        </div>
      </div>

      {/* Search Bar */}
      <div className="flex items-center justify-between p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder={activeTab === 'rfqs' ? "Search requests..." : "Search purchase orders..."}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
          />
        </div>
      </div>

      {/* ── TAB 1: PRICE REQUESTS (RFQs) ── */}
      {activeTab === 'rfqs' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 font-bold uppercase text-[11px] border-b border-slate-200">
                  <tr>
                    <th className="px-5 py-3.5">Request No.</th>
                    <th className="px-5 py-3.5">Product</th>
                    <th className="px-5 py-3.5">Quantity</th>
                    <th className="px-5 py-3.5">Needed By</th>
                    <th className="px-5 py-3.5">Status</th>
                    <th className="px-5 py-3.5">Quotes</th>
                    <th className="px-5 py-3.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {rfqs
                    .filter((r) =>
                      (r.rfq_number || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                      (r.status || '').toLowerCase().includes(searchTerm.toLowerCase())
                    )
                    .map((rfq) => {
                      const rQuotes = quotes.filter((q) => q.rfq_id === rfq.id || q.rfq_id === rfq.rfq_number);
                      const isDraft = rfq.status === 'PENDING' || rfq.status === 'DRAFT';

                      return (
                        <tr key={rfq.id} className="hover:bg-slate-50/60 transition-colors">
                          <td className="px-5 py-3.5 font-mono font-bold text-slate-900">
                            {rfq.rfq_number || `RFQ-${rfq.id}`}
                          </td>
                          <td className="px-5 py-3.5 font-semibold text-slate-900">
                            {getProductName(rfq.product_id)}
                          </td>
                          <td className="px-5 py-3.5 font-mono text-slate-700">
                            {(rfq.quantity || 1000).toLocaleString()} units
                          </td>
                          <td className="px-5 py-3.5 text-slate-600 font-medium">
                            {rfq.needed_by || 'Flexible'}
                          </td>
                          <td className="px-5 py-3.5">
                            <StatusBadge status={rfq.status} />
                          </td>
                          <td className="px-5 py-3.5">
                            <button
                              onClick={() => setSelectedRfqForQuotes(rfq)}
                              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-bold bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200"
                            >
                              <FileCheck className="w-3.5 h-3.5" />
                              {rQuotes.length} Quotes
                            </button>
                          </td>
                          <td className="px-5 py-3.5 text-right space-x-1.5">
                            {isDraft && (
                              <button
                                onClick={() => handleOpenEditRfq(rfq)}
                                className="px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded border border-slate-200"
                              >
                                Edit
                              </button>
                            )}
                            {isDraft && (
                              <button
                                onClick={() => handleCancelRfq(rfq)}
                                className="px-2.5 py-1 text-xs font-semibold text-amber-700 hover:bg-amber-50 rounded border border-amber-200"
                              >
                                Cancel
                              </button>
                            )}
                            {isDraft && (
                              <button
                                onClick={() =>
                                  setDeleteDialog({
                                    isOpen: true,
                                    itemType: 'rfq',
                                    item: rfq,
                                  })
                                }
                                className="px-2.5 py-1 text-xs font-semibold text-rose-600 hover:bg-rose-50 rounded border border-rose-200"
                              >
                                Delete
                              </button>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                </tbody>
              </table>
            </div>

            {rfqs.length === 0 && !loading && (
              <div className="p-8">
                <EmptyState
                  message="No price requests created yet."
                  actionLabel="+ Create your first price request"
                  onAction={handleOpenAddRfq}
                />
              </div>
            )}
          </div>

          {/* Supplier Quotes for Selected RFQ */}
          {selectedRfqForQuotes && (
            <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div>
                  <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                    <FileCheck className="w-5 h-5 text-[#8e3a59]" />
                    Supplier Replies for {selectedRfqForQuotes.rfq_number || `RFQ-${selectedRfqForQuotes.id}`}
                  </h3>
                  <p className="text-xs text-slate-500">
                    Product: {getProductName(selectedRfqForQuotes.product_id)} · Needed: {selectedRfqForQuotes.quantity} units
                  </p>
                </div>
                <button
                  onClick={() => setSelectedRfqForQuotes(null)}
                  className="text-slate-400 hover:text-slate-600"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {quotes.filter((q) => q.rfq_id === selectedRfqForQuotes.id || q.rfq_id === selectedRfqForQuotes.rfq_number).length === 0 ? (
                <p className="text-xs text-slate-500 py-4 text-center">
                  No quotes submitted by suppliers yet for this request.
                </p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {quotes
                    .filter((q) => q.rfq_id === selectedRfqForQuotes.id || q.rfq_id === selectedRfqForQuotes.rfq_number)
                    .map((quote) => (
                      <div key={quote.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-slate-900">{getSupplierName(quote.supplier_id)}</span>
                          <StatusBadge status={quote.status} />
                        </div>
                        <div className="text-xs space-y-1">
                          <div className="flex justify-between">
                            <span className="text-slate-500">Quoted Price:</span>
                            <span className="font-bold font-mono text-slate-900">{formatINR(quote.price, 2)} / unit</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-500">Available Qty:</span>
                            <span className="font-semibold text-slate-800">{(quote.quantity || 1000).toLocaleString()}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-500">Delivery Days:</span>
                            <span className="font-semibold text-slate-800">{quote.delivery_days || 10} days</span>
                          </div>
                        </div>

                        {quote.status !== 'ACCEPTED' && quote.status !== 'REJECTED' && (
                          <div className="flex items-center gap-2 pt-2 border-t border-slate-200">
                            <button
                              onClick={() => handleAcceptQuote(quote)}
                              className="flex-1 py-1.5 rounded-lg text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 transition-colors flex items-center justify-center gap-1"
                            >
                              <CheckCircle className="w-3.5 h-3.5" />
                              Accept Quote
                            </button>
                            <button
                              onClick={() => handleRejectQuote(quote)}
                              className="flex-1 py-1.5 rounded-lg text-xs font-bold text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 transition-colors flex items-center justify-center gap-1"
                            >
                              <XCircle className="w-3.5 h-3.5" />
                              Reject
                            </button>
                          </div>
                        )}
                      </div>
                    ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ── TAB 2: PURCHASE ORDERS ── */}
      {activeTab === 'orders' && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 font-bold uppercase text-[11px] border-b border-slate-200">
                <tr>
                  <th className="px-5 py-3.5">PO Number</th>
                  <th className="px-5 py-3.5">Supplier</th>
                  <th className="px-5 py-3.5">Total Amount</th>
                  <th className="px-5 py-3.5">Order Date</th>
                  <th className="px-5 py-3.5">Status</th>
                  <th className="px-5 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {purchaseOrders
                  .filter((po) =>
                    (po.po_number || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                    (po.status || '').toLowerCase().includes(searchTerm.toLowerCase())
                  )
                  .map((po) => {
                    const isDraft = po.status === 'DRAFT' || po.status === 'PENDING';

                    return (
                      <tr key={po.id} className="hover:bg-slate-50/60 transition-colors">
                        <td className="px-5 py-3.5 font-mono font-bold text-slate-900">
                          {po.po_number}
                        </td>
                        <td className="px-5 py-3.5 font-semibold text-slate-900">
                          {getSupplierName(po.supplier_id)}
                        </td>
                        <td className="px-5 py-3.5 font-mono font-bold text-slate-900">
                          {formatINR(po.total_amount, 2)}
                        </td>
                        <td className="px-5 py-3.5 text-slate-600 font-medium">
                          {po.order_date || 'Recent'}
                        </td>
                        <td className="px-5 py-3.5">
                          <StatusBadge status={po.status} />
                        </td>
                        <td className="px-5 py-3.5 text-right space-x-1.5">
                          {isDraft && (
                            <button
                              onClick={() => handleApprovePo(po)}
                              className="px-2.5 py-1 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded shadow-sm"
                            >
                              Approve
                            </button>
                          )}
                          {isDraft && (
                            <button
                              onClick={() => handleOpenEditPo(po)}
                              className="px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded border border-slate-200"
                            >
                              Edit
                            </button>
                          )}
                          {isDraft && (
                            <button
                              onClick={() => handleCancelPo(po)}
                              className="px-2.5 py-1 text-xs font-semibold text-amber-700 hover:bg-amber-50 rounded border border-amber-200"
                            >
                              Cancel
                            </button>
                          )}
                          {isDraft && (
                            <button
                              onClick={() =>
                                setDeleteDialog({
                                  isOpen: true,
                                  itemType: 'po',
                                  item: po,
                                })
                              }
                              className="px-2.5 py-1 text-xs font-semibold text-rose-600 hover:bg-rose-50 rounded border border-rose-200"
                            >
                              Delete
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>

          {purchaseOrders.length === 0 && !loading && (
            <div className="p-8">
              <EmptyState
                message="No purchase orders recorded."
                actionLabel="+ Create your first purchase order"
                onAction={handleOpenAddPo}
              />
            </div>
          )}
        </div>
      )}

      {/* New / Edit RFQ Modal */}
      {showRfqModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="w-full max-w-lg bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">
                {editingRfq ? 'Edit Price Request' : '+ New Price Request'}
              </h3>
              <button
                onClick={() => setShowRfqModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSaveRfq} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Select Product</label>
                <select
                  value={rfqForm.product_id}
                  onChange={(e) => setRfqForm({ ...rfqForm, product_id: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                >
                  {products.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.sku})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Quantity Needed</label>
                <input
                  type="number"
                  value={rfqForm.quantity}
                  onChange={(e) => setRfqForm({ ...rfqForm, quantity: e.target.value })}
                  required
                  min="1"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Needed-By Date</label>
                <input
                  type="date"
                  value={rfqForm.needed_by}
                  onChange={(e) => setRfqForm({ ...rfqForm, needed_by: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowRfqModal(false)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-100 border border-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-[#8e3a59] hover:bg-[#782f49] shadow-sm"
                >
                  Save Request
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* New / Edit PO Modal */}
      {showPoModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="w-full max-w-lg bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">
                {editingPo ? 'Edit Purchase Order' : '+ New Purchase Order'}
              </h3>
              <button
                onClick={() => setShowPoModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSavePo} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">PO Number</label>
                <input
                  type="text"
                  value={poForm.po_number}
                  onChange={(e) => setPoForm({ ...poForm, po_number: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Supplier</label>
                <select
                  value={poForm.supplier_id}
                  onChange={(e) => setPoForm({ ...poForm, supplier_id: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                >
                  {suppliers.map((s) => (
                    <option key={s.id || s.code} value={s.code || s.id}>
                      {s.name} ({s.code})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Total Amount (₹)</label>
                <input
                  type="number"
                  step="0.01"
                  value={poForm.total_amount}
                  onChange={(e) => setPoForm({ ...poForm, total_amount: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Status</label>
                <select
                  value={poForm.status}
                  onChange={(e) => setPoForm({ ...poForm, status: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                >
                  <option value="DRAFT">Draft</option>
                  <option value="APPROVED">Approved</option>
                  <option value="CANCELLED">Cancelled</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowPoModal(false)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-100 border border-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-[#8e3a59] hover:bg-[#782f49] shadow-sm"
                >
                  Save Order
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Dialog */}
      <DeleteConfirmDialog
        isOpen={deleteDialog.isOpen}
        itemName={deleteDialog.item?.po_number || deleteDialog.item?.rfq_number || 'this item'}
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
