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
  Package,
  Plus,
  Search,
  Edit2,
  Trash2,
  RefreshCw,
  X,
  Filter,
} from 'lucide-react';

export const ProductsPage = ({ mode = 'admin' }) => {
  const { user } = useApp();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');

  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [form, setForm] = useState({
    sku: '',
    name: '',
    category: 'Electronics',
    unit_cost: 100,
    selling_price: 150,
  });

  // Delete State
  const [deleteDialog, setDeleteDialog] = useState({
    isOpen: false,
    item: null,
  });

  const loadProducts = async () => {
    setLoading(true);
    try {
      const data = await RimberioAPI.getProducts();
      setProducts(Array.isArray(data) ? data : []);
    } catch (err) {
      setToastMessage('Could not load products from server');
      setToastType('error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, []);

  const handleOpenAdd = () => {
    setEditingProduct(null);
    setForm({
      sku: `PRD-${Math.floor(1000 + Math.random() * 9000)}`,
      name: '',
      category: 'Electronics',
      unit_cost: 100,
      selling_price: 150,
    });
    setShowModal(true);
  };

  const handleOpenEdit = (p) => {
    setEditingProduct(p);
    setForm({
      sku: p.sku || '',
      name: p.name || '',
      category: p.category || 'Electronics',
      unit_cost: p.unit_cost || 0,
      selling_price: p.selling_price || 0,
    });
    setShowModal(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.sku || !form.name) {
      setToastMessage('Product code and name are required.');
      setToastType('error');
      return;
    }

    try {
      if (editingProduct) {
        await RimberioAPI.updateProduct(editingProduct.id, {
          sku: form.sku,
          name: form.name,
          category: form.category,
          unit_cost: parseFloat(form.unit_cost),
          selling_price: parseFloat(form.selling_price),
        });
        setToastMessage(`Product "${form.name}" updated successfully.`);
      } else {
        await RimberioAPI.createProduct({
          sku: form.sku,
          name: form.name,
          category: form.category,
          unit_cost: parseFloat(form.unit_cost),
          selling_price: parseFloat(form.selling_price),
        });
        setToastMessage(`Product "${form.name}" added successfully.`);
      }
      setToastType('success');
      setShowModal(false);
      loadProducts();
    } catch (err) {
      setToastMessage(err.message || 'Operation failed');
      setToastType('error');
    }
  };

  const confirmDelete = async () => {
    if (!deleteDialog.item) return;
    try {
      await RimberioAPI.deleteProduct(deleteDialog.item.id);
      setToastMessage(`Product "${deleteDialog.item.name}" deleted.`);
      setToastType('success');
      setDeleteDialog({ isOpen: false, item: null });
      loadProducts();
    } catch (err) {
      setToastMessage(err.message || 'Failed to delete product');
      setToastType('error');
    }
  };

  const categories = ['ALL', ...Array.from(new Set(products.map((p) => p.category).filter(Boolean)))];

  const filteredProducts = products.filter((p) => {
    const matchesSearch =
      (p.name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (p.sku || '').toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter === 'ALL' || p.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-xl bg-white border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider bg-[#8e3a59]/10 text-[#8e3a59]">
              <Package className="w-3.5 h-3.5" />
              Products Catalog
            </span>
          </div>
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              {mode === 'buyer' ? 'My Products' : 'Products'}
            </h1>
            <HelpTooltip text="Manage catalog products, unit cost, and selling price." />
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            View, add, update, and manage products and inventory items.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadProducts}
            disabled={loading}
            className="px-3.5 py-2 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 transition-colors flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            onClick={handleOpenAdd}
            className="px-4 py-2 rounded-lg bg-[#8e3a59] hover:bg-[#782f49] text-white text-xs font-bold shadow-sm transition-colors flex items-center gap-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            + Add Product
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Total Products</span>
          <div className="text-2xl font-bold text-slate-900 mt-1">{products.length}</div>
          <p className="text-[11px] text-slate-400 mt-0.5">Active catalog items</p>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Categories</span>
          <div className="text-2xl font-bold text-slate-900 mt-1">{categories.length - 1}</div>
          <p className="text-[11px] text-slate-400 mt-0.5">Distinct categories</p>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Avg Unit Cost</span>
          <div className="text-2xl font-bold text-slate-900 mt-1">
            {products.length > 0
              ? formatINR(
                  products.reduce((acc, p) => acc + (Number(p.unit_cost) || 0), 0) / products.length,
                  0
                )
              : '₹0'}
          </div>
          <p className="text-[11px] text-slate-400 mt-0.5">Purchase cost baseline</p>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Avg Selling Price</span>
          <div className="text-2xl font-bold text-slate-900 mt-1">
            {products.length > 0
              ? formatINR(
                  products.reduce((acc, p) => acc + (Number(p.selling_price) || 0), 0) /
                    products.length,
                  0
                )
              : '₹0'}
          </div>
          <p className="text-[11px] text-slate-400 mt-0.5">Commercial catalog price</p>
        </div>
      </div>

      {/* Search & Filter */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by name or product code..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <span className="text-xs text-slate-500 font-medium">Category:</span>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="text-xs border border-slate-200 rounded-lg px-3 py-2 bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
          >
            {categories.map((c) => (
              <option key={c} value={c}>
                {c === 'ALL' ? 'All Categories' : c}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 font-bold uppercase text-[11px] border-b border-slate-200">
              <tr>
                <th className="px-5 py-3.5">Product Code</th>
                <th className="px-5 py-3.5">Name</th>
                <th className="px-5 py-3.5">Category</th>
                <th className="px-5 py-3.5">Unit Cost</th>
                <th className="px-5 py-3.5">Selling Price</th>
                <th className="px-5 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredProducts.map((p) => (
                <tr key={p.id || p.sku} className="hover:bg-slate-50/60 transition-colors">
                  <td className="px-5 py-3.5 font-mono font-bold text-slate-900">{p.sku}</td>
                  <td className="px-5 py-3.5 font-semibold text-slate-900">{p.name}</td>
                  <td className="px-5 py-3.5">
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-700">
                      {p.category || 'General'}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 font-mono text-slate-700">
                    {formatINR(p.unit_cost, 2)}
                  </td>
                  <td className="px-5 py-3.5 font-mono text-emerald-700 font-bold">
                    {formatINR(p.selling_price, 2)}
                  </td>
                  <td className="px-5 py-3.5 text-right space-x-2">
                    <button
                      onClick={() => handleOpenEdit(p)}
                      className="px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded border border-slate-200"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() =>
                        setDeleteDialog({
                          isOpen: true,
                          item: p,
                        })
                      }
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

        {filteredProducts.length === 0 && !loading && (
          <div className="p-8">
            <EmptyState
              message="No products found."
              actionLabel="+ Add your first product"
              onAction={handleOpenAdd}
            />
          </div>
        )}
      </div>

      {/* Add / Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="w-full max-w-lg bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">
                {editingProduct ? 'Edit Product' : '+ Add Product'}
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
                <label className="block text-slate-700 font-semibold mb-1">Product Code</label>
                <input
                  type="text"
                  value={form.sku}
                  onChange={(e) => setForm({ ...form, sku: e.target.value })}
                  placeholder="e.g. PRD-1001"
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Product Name</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="e.g. High-Voltage Ceramic Capacitor"
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Category</label>
                <input
                  type="text"
                  value={form.category}
                  onChange={(e) => setForm({ ...form, category: e.target.value })}
                  placeholder="e.g. Electronics, Microchips, Hardware"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Unit Cost (₹)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={form.unit_cost}
                    onChange={(e) => setForm({ ...form, unit_cost: e.target.value })}
                    placeholder="100.00"
                    required
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Selling Price (₹)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={form.selling_price}
                    onChange={(e) => setForm({ ...form, selling_price: e.target.value })}
                    placeholder="150.00"
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
                  Save Product
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <DeleteConfirmDialog
        isOpen={deleteDialog.isOpen}
        itemName={deleteDialog.item?.name}
        onConfirm={confirmDelete}
        onCancel={() => setDeleteDialog({ isOpen: false, item: null })}
      />

      {/* Toast Notification */}
      <Toast
        message={toastMessage}
        type={toastType}
        onClose={() => setToastMessage('')}
      />
    </div>
  );
};
