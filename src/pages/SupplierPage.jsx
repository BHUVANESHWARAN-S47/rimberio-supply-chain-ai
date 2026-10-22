import React, { useState, useEffect } from 'react';
import {
  Building2,
  Users,
  MapPin,
  Plus,
  Edit2,
  Trash2,
  RotateCcw,
  Search,
  CheckCircle,
  HelpCircle,
  X,
  Filter,
  CheckSquare,
  Square,
  ArrowRight,
  TrendingUp,
} from 'lucide-react';
import { RimberioAPI } from '../services/api';
import { useApp } from '../context/AppContext';
import { formatINR } from '../utils/currency';
import {
  HelpTooltip,
  StatusBadge,
  DeleteConfirmDialog,
  EmptyState,
  Toast,
} from '../components/common/CommonUI';

export const SupplierPage = ({ mode = 'buyer' }) => {
  const { setCurrentPage } = useApp();
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [selectedSuppliers, setSelectedSuppliers] = useState([]);
  const [showCompareModal, setShowCompareModal] = useState(false);

  // Toast
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');

  // Modals
  const [showModal, setShowModal] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState(null);
  const [form, setForm] = useState({
    name: '',
    country: 'India',
    unit_cost: 140,
    quality_score: 95,
    avg_delivery_days: 10,
    capacity_monthly: 50000,
  });

  // Delete
  const [deleteDialog, setDeleteDialog] = useState({
    isOpen: false,
    item: null,
  });

  const fetchSuppliers = async () => {
    setLoading(true);
    try {
      const data = await RimberioAPI.getSuppliers();
      if (Array.isArray(data) && data.length > 0) {
        setSuppliers(data);
      } else {
        setSuppliers([]);
      }
    } catch (err) {
      setToastMessage('Could not load suppliers from server');
      setToastType('error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSuppliers();
  }, []);

  const handleOpenAdd = () => {
    setEditingSupplier(null);
    setForm({
      name: '',
      country: 'India Hub',
      unit_cost: 140,
      quality_score: 95,
      avg_delivery_days: 10,
      capacity_monthly: 50000,
    });
    setShowModal(true);
  };

  const handleOpenEdit = (s) => {
    setEditingSupplier(s);
    setForm({
      name: s.name || '',
      country: s.country || 'India Hub',
      unit_cost: s.unit_cost || 140,
      quality_score: s.quality_score || 95,
      avg_delivery_days: s.avg_delivery_days || 10,
      capacity_monthly: s.capacity_monthly || 50000,
    });
    setShowModal(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.name) {
      setToastMessage('Supplier name is required');
      setToastType('error');
      return;
    }

    try {
      if (editingSupplier) {
        await RimberioAPI.updateSupplier(editingSupplier.code || editingSupplier.id, {
          name: form.name,
          country: form.country,
          unit_cost: parseFloat(form.unit_cost),
          quality_score: parseFloat(form.quality_score),
          avg_delivery_days: parseInt(form.avg_delivery_days, 10),
          capacity_monthly: parseInt(form.capacity_monthly, 10),
        });
        setToastMessage(`Supplier "${form.name}" updated successfully.`);
      } else {
        const newCode = `SUP-${Math.floor(100 + Math.random() * 900)}`;
        await RimberioAPI.createSupplier({
          code: newCode,
          name: form.name,
          country: form.country,
          unit_cost: parseFloat(form.unit_cost),
          quality_score: parseFloat(form.quality_score),
          avg_delivery_days: parseInt(form.avg_delivery_days, 10),
          capacity_monthly: parseInt(form.capacity_monthly, 10),
          tier: 'Tier-1',
          risk_score: 20,
          on_time_delivery_rate: 95,
        });
        setToastMessage(`Supplier "${form.name}" added successfully.`);
      }
      setToastType('success');
      setShowModal(false);
      fetchSuppliers();
    } catch (err) {
      setToastMessage(err.message || 'Operation failed');
      setToastType('error');
    }
  };

  const confirmDelete = async () => {
    if (!deleteDialog.item) return;
    try {
      await RimberioAPI.deleteSupplier(deleteDialog.item.code || deleteDialog.item.id);
      setToastMessage(`Supplier "${deleteDialog.item.name}" deleted.`);
      setToastType('success');
      setDeleteDialog({ isOpen: false, item: null });
      fetchSuppliers();
    } catch (err) {
      setToastMessage(err.message || 'Failed to delete supplier');
      setToastType('error');
    }
  };

  const handleResetKaggle = async () => {
    setLoading(true);
    try {
      await RimberioAPI.resetSuppliersToKaggle();
      setToastMessage('Benchmark suppliers reloaded successfully.');
      setToastType('success');
      fetchSuppliers();
    } catch (err) {
      setToastMessage('Failed to reload sample data');
      setToastType('error');
      setLoading(false);
    }
  };

  const toggleSelectSupplier = (supplier) => {
    const isSelected = selectedSuppliers.some((s) => (s.id || s.code) === (supplier.id || supplier.code));
    if (isSelected) {
      setSelectedSuppliers(selectedSuppliers.filter((s) => (s.id || s.code) !== (supplier.id || supplier.code)));
    } else {
      if (selectedSuppliers.length >= 3) {
        setToastMessage('You can compare a maximum of 3 suppliers at a time.');
        setToastType('error');
        return;
      }
      setSelectedSuppliers([...selectedSuppliers, supplier]);
    }
  };

  const getRiskLabel = (score) => {
    const val = Number(score) || 0;
    if (val < 30) return { label: 'Low', color: 'text-emerald-700 bg-emerald-50 border-emerald-200' };
    if (val < 60) return { label: 'Medium', color: 'text-amber-700 bg-amber-50 border-amber-200' };
    return { label: 'High', color: 'text-rose-700 bg-rose-50 border-rose-200' };
  };

  const filteredSuppliers = suppliers.filter((s) => {
    const matchesSearch =
      (s.name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (s.country || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (s.code || '').toLowerCase().includes(searchTerm.toLowerCase());

    const risk = getRiskLabel(s.risk_score).label.toUpperCase();
    const matchesRisk = riskFilter === 'ALL' || risk === riskFilter;

    return matchesSearch && matchesRisk;
  });

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-xl bg-white border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider bg-[#8e3a59]/10 text-[#8e3a59]">
              <Building2 className="w-3.5 h-3.5" />
              Approved Suppliers
            </span>
          </div>
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              {mode === 'admin' ? 'Suppliers' : 'Find Suppliers'}
            </h1>
            <HelpTooltip text="Search, compare, and manage verified suppliers with live quality and delivery metrics." />
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Tick up to 3 suppliers to compare them side by side, or request price bids directly.
          </p>
        </div>

        <div className="flex items-center flex-wrap gap-3">
          <button
            onClick={handleResetKaggle}
            disabled={loading}
            className="px-3.5 py-2 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 transition-colors flex items-center gap-1.5"
            title="Reset to 20 benchmark vendors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Reload Sample Data
          </button>
          <button
            onClick={fetchSuppliers}
            disabled={loading}
            className="px-3.5 py-2 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 transition-colors flex items-center gap-1.5"
          >
            Refresh
          </button>
          <button
            onClick={handleOpenAdd}
            className="px-4 py-2 rounded-lg bg-[#8e3a59] hover:bg-[#782f49] text-white text-xs font-bold shadow-sm transition-colors flex items-center gap-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            + Add Supplier
          </button>
        </div>
      </div>

      {/* 4 Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Total Suppliers</span>
          <div className="text-2xl font-bold text-slate-900 mt-1">{suppliers.length}</div>
          <p className="text-[11px] text-slate-400 mt-0.5">Approved partner network</p>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Avg Delivery Days</span>
          <div className="text-2xl font-bold text-slate-900 mt-1">
            {suppliers.length > 0
              ? Math.round(
                  suppliers.reduce((acc, s) => acc + (Number(s.avg_delivery_days) || 12), 0) /
                    suppliers.length
                )
              : 0}{' '}
            days
          </div>
          <p className="text-[11px] text-slate-400 mt-0.5">Across active manufacturing hubs</p>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Avg Quality Score</span>
          <div className="text-2xl font-bold text-emerald-700 mt-1">
            {suppliers.length > 0
              ? (
                  suppliers.reduce((acc, s) => acc + (Number(s.quality_score) || 95), 0) /
                  suppliers.length
                ).toFixed(1)
              : '0'}
            %
          </div>
          <p className="text-[11px] text-slate-400 mt-0.5">Defect-free rate</p>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Selected to Compare</span>
          <div className="text-2xl font-bold text-[#8e3a59] mt-1">{selectedSuppliers.length} / 3</div>
          <p className="text-[11px] text-slate-400 mt-0.5">
            {selectedSuppliers.length >= 2 ? 'Ready for side-by-side' : 'Tick 2 or 3 in the table'}
          </p>
        </div>
      </div>

      {/* Comparison Drawer / Banner if >= 2 selected */}
      {selectedSuppliers.length >= 2 && (
        <div className="p-5 rounded-xl bg-gradient-to-r from-[#8e3a59]/10 via-[#8e3a59]/5 to-transparent border border-[#8e3a59]/30 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-[#8e3a59]" />
              Comparing {selectedSuppliers.length} Suppliers Side-by-Side
            </h3>
            <p className="text-xs text-slate-600 mt-0.5">
              {selectedSuppliers.map((s) => s.name).join(' vs ')}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSelectedSuppliers([])}
              className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs font-semibold text-slate-600 hover:bg-slate-50"
            >
              Clear Selection
            </button>
            <button
              onClick={() => setShowCompareModal(true)}
              className="px-4 py-1.5 rounded-lg bg-[#8e3a59] hover:bg-[#782f49] text-white text-xs font-bold shadow-sm flex items-center gap-1.5"
            >
              View Comparison
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search suppliers by name or country..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
          />
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <span className="text-xs text-slate-500 font-medium">Risk Filter:</span>
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="text-xs border border-slate-200 rounded-lg px-3 py-2 bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
          >
            <option value="ALL">All Risk Levels</option>
            <option value="LOW">Low Risk</option>
            <option value="MEDIUM">Medium Risk</option>
            <option value="HIGH">High Risk</option>
          </select>
        </div>
      </div>

      {/* Main Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 font-bold uppercase text-[11px] border-b border-slate-200">
              <tr>
                <th className="px-4 py-3.5 text-center w-12">Compare</th>
                <th className="px-4 py-3.5">Supplier Name</th>
                <th className="px-4 py-3.5">Location</th>
                <th className="px-4 py-3.5">Price / Unit</th>
                <th className="px-4 py-3.5">Quality</th>
                <th className="px-4 py-3.5">Delivery Days</th>
                <th className="px-4 py-3.5">Supplier Risk</th>
                <th className="px-4 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredSuppliers.map((s) => {
                const isSelected = selectedSuppliers.some(
                  (sel) => (sel.id || sel.code) === (s.id || s.code)
                );
                const risk = getRiskLabel(s.risk_score);

                return (
                  <tr
                    key={s.id || s.code}
                    className={`hover:bg-slate-50/60 transition-colors ${
                      isSelected ? 'bg-[#8e3a59]/5' : ''
                    }`}
                  >
                    <td className="px-4 py-3.5 text-center">
                      <button
                        type="button"
                        onClick={() => toggleSelectSupplier(s)}
                        className="text-slate-500 hover:text-[#8e3a59]"
                        title="Tick to compare"
                      >
                        {isSelected ? (
                          <CheckSquare className="w-4 h-4 text-[#8e3a59]" />
                        ) : (
                          <Square className="w-4 h-4 text-slate-300" />
                        )}
                      </button>
                    </td>
                    <td className="px-4 py-3.5">
                      <div className="font-semibold text-slate-900">{s.name}</div>
                      <div className="font-mono text-[10px] text-slate-400">{s.code}</div>
                    </td>
                    <td className="px-4 py-3.5 text-slate-600">{s.country || 'India'}</td>
                    <td className="px-4 py-3.5 font-mono font-bold text-slate-900">
                      {formatINR(s.unit_cost || 140, 2)}
                    </td>
                    <td className="px-4 py-3.5">
                      <span className="font-semibold text-emerald-700">
                        {Number(s.quality_score || 95).toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-slate-700 font-medium">
                      {s.avg_delivery_days || 10} days
                    </td>
                    <td className="px-4 py-3.5">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold border ${risk.color}`}
                      >
                        {risk.label}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-right space-x-1.5">
                      <button
                        onClick={() => setCurrentPage('rfqs')}
                        className="px-2.5 py-1 text-xs font-semibold text-[#8e3a59] hover:bg-[#8e3a59]/10 rounded border border-[#8e3a59]/30"
                        title="Request price quotation"
                      >
                        Request Price
                      </button>
                      <button
                        onClick={() => handleOpenEdit(s)}
                        className="px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded border border-slate-200"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => setDeleteDialog({ isOpen: true, item: s })}
                        className="px-2.5 py-1 text-xs font-semibold text-rose-600 hover:bg-rose-50 rounded border border-rose-200"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {filteredSuppliers.length === 0 && !loading && (
          <div className="p-8">
            <EmptyState
              message="No suppliers found."
              actionLabel="+ Add your first supplier"
              onAction={handleOpenAdd}
            />
          </div>
        )}
      </div>

      {/* Side-by-Side Comparison Modal */}
      {showCompareModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="w-full max-w-4xl bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-base font-bold text-slate-900">Side-by-Side Supplier Comparison</h3>
                <p className="text-xs text-slate-500">Compare price, quality, delivery days, and supplier risk</p>
              </div>
              <button
                onClick={() => setShowCompareModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {selectedSuppliers.map((s, idx) => {
                const risk = getRiskLabel(s.risk_score);
                return (
                  <div key={s.id || s.code} className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold text-[#8e3a59] uppercase tracking-wider">
                        Option #{idx + 1}
                      </span>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${risk.color}`}>
                        {risk.label} Risk
                      </span>
                    </div>

                    <h4 className="text-sm font-bold text-slate-900 leading-snug">{s.name}</h4>
                    <p className="text-xs text-slate-500 font-mono">{s.country || 'India Hub'}</p>

                    <div className="pt-2 border-t border-slate-200 space-y-2 text-xs">
                      <div className="flex justify-between">
                        <span className="text-slate-500">Price per unit:</span>
                        <span className="font-bold font-mono text-slate-900">{formatINR(s.unit_cost || 140, 2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">Quality score:</span>
                        <span className="font-bold text-emerald-700">{Number(s.quality_score || 95).toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">Delivery days:</span>
                        <span className="font-bold text-slate-800">{s.avg_delivery_days || 10} days</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">Monthly capacity:</span>
                        <span className="font-bold text-slate-800">{(s.capacity_monthly || 50000).toLocaleString()} units</span>
                      </div>
                    </div>

                    <div className="pt-3">
                      <button
                        onClick={() => {
                          setShowCompareModal(false);
                          setCurrentPage('rfqs');
                        }}
                        className="w-full py-2 rounded-lg bg-[#8e3a59] hover:bg-[#782f49] text-white text-xs font-bold transition-colors"
                      >
                        Request Price from {s.name.split(' ')[0]}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setShowCompareModal(false)}
                className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add / Edit Supplier Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="w-full max-w-lg bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">
                {editingSupplier ? 'Edit Supplier' : '+ Add Supplier'}
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSave} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Supplier Name</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="e.g. Apex Precision Systems"
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Country / Hub</label>
                <input
                  type="text"
                  value={form.country}
                  onChange={(e) => setForm({ ...form, country: e.target.value })}
                  placeholder="e.g. Bengaluru / Karnataka, India"
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
                    value={form.unit_cost}
                    onChange={(e) => setForm({ ...form, unit_cost: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Quality Score (%)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={form.quality_score}
                    onChange={(e) => setForm({ ...form, quality_score: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Delivery Days</label>
                  <input
                    type="number"
                    value={form.avg_delivery_days}
                    onChange={(e) => setForm({ ...form, avg_delivery_days: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Monthly Capacity (units)</label>
                  <input
                    type="number"
                    value={form.capacity_monthly}
                    onChange={(e) => setForm({ ...form, capacity_monthly: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-100 border border-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-[#8e3a59] hover:bg-[#782f49] shadow-sm"
                >
                  Save Supplier
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Dialog */}
      <DeleteConfirmDialog
        isOpen={deleteDialog.isOpen}
        itemName={deleteDialog.item?.name}
        onConfirm={confirmDelete}
        onCancel={() => setDeleteDialog({ isOpen: false, item: null })}
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
