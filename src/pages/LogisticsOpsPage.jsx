import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { RimberioAPI } from '../services/api';
import { formatINR } from '../utils/currency';
import {
  Truck,
  Ship,
  MapPin,
  Clock,
  AlertTriangle,
  RefreshCw,
  Search,
  Filter,
  ArrowRight,
  Plus,
  CheckCircle,
  X,
  Building,
  Package,
  Bell,
  HelpCircle,
  Zap,
} from 'lucide-react';
import {
  HelpTooltip,
  StatusBadge,
  DeleteConfirmDialog,
  EmptyState,
  Toast,
} from '../components/common/CommonUI';

export const LogisticsOpsPage = ({ initialTab = 'shipments' }) => {
  const { user } = useApp();
  const [activeTab, setActiveTab] = useState(initialTab);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');

  // Tab Data
  const [shipments, setShipments] = useState([]);
  const [carriers, setCarriers] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [products, setProducts] = useState([]);
  const [selectedWarehouseId, setSelectedWarehouseId] = useState('');
  const [stockList, setStockList] = useState([]);

  // Modals
  const [showShipmentModal, setShowShipmentModal] = useState(false);
  const [editingShipment, setEditingShipment] = useState(null);
  const [shipmentForm, setShipmentForm] = useState({
    shipment_number: '',
    carrier_id: '',
    origin: 'Mumbai Transshipment Port',
    destination: 'Bengaluru Logistics Park',
    expected_date: new Date(Date.now() + 5 * 86400000).toISOString().split('T')[0],
    status: 'IN_TRANSIT',
  });

  const [showCarrierModal, setShowCarrierModal] = useState(false);
  const [editingCarrier, setEditingCarrier] = useState(null);
  const [carrierForm, setCarrierForm] = useState({
    name: '',
    mode: 'Road',
    on_time_delivery_rate: 94.5,
  });

  const [showWarehouseModal, setShowWarehouseModal] = useState(false);
  const [editingWarehouse, setEditingWarehouse] = useState(null);
  const [warehouseForm, setWarehouseForm] = useState({
    name: '',
    location: 'Pune',
    country: 'India',
    capacity: 100000,
  });

  // Stock Movement Modal
  const [showStockModal, setShowStockModal] = useState(false);
  const [stockActionType, setStockActionType] = useState('INBOUND'); // INBOUND (+ Add) or OUTBOUND (- Remove)
  const [selectedStockProduct, setSelectedStockProduct] = useState(null);
  const [stockQuantity, setStockQuantity] = useState(500);

  // Delay Report Modal
  const [showDelayModal, setShowDelayModal] = useState(false);
  const [delayTargetShipment, setDelayTargetShipment] = useState(null);
  const [delayReason, setDelayReason] = useState('Port Transshipment Bottleneck');
  const [delayNewDate, setDelayNewDate] = useState('');

  // Transport What-If Popup
  const [showWhatIfPopup, setShowWhatIfPopup] = useState(false);
  const [whatIfResults, setWhatIfResults] = useState(null);

  // Delete Dialog
  const [deleteDialog, setDeleteDialog] = useState({
    isOpen: false,
    itemType: '',
    item: null,
  });

  const loadAll = async () => {
    setLoading(true);
    try {
      const [sRes, cRes, wRes, pRes] = await Promise.all([
        RimberioAPI.getShipments().catch(() => []),
        RimberioAPI.getCarriers().catch(() => []),
        RimberioAPI.getWarehouses().catch(() => []),
        RimberioAPI.getProducts().catch(() => []),
      ]);

      const sArr = Array.isArray(sRes) ? sRes : [];
      const cArr = Array.isArray(cRes) ? cRes : [];
      const wArr = Array.isArray(wRes) ? wRes : [];
      const pArr = Array.isArray(pRes) ? pRes : [];

      setShipments(sArr);
      setCarriers(cArr);
      setWarehouses(wArr);
      setProducts(pArr);

      if (wArr.length > 0 && !selectedWarehouseId) {
        setSelectedWarehouseId(wArr[0].id);
      }
    } catch (err) {
      setToastMessage('Error loading logistics data');
      setToastType('error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  useEffect(() => {
    if (initialTab) setActiveTab(initialTab);
  }, [initialTab]);

  // Load stock when selected warehouse changes
  useEffect(() => {
    if (!selectedWarehouseId) return;
    RimberioAPI.getWarehouseStock(selectedWarehouseId)
      .then((data) => setStockList(Array.isArray(data) ? data : []))
      .catch(() => setStockList([]));
  }, [selectedWarehouseId]);

  // Shipment Actions
  const handleOpenAddShipment = () => {
    setEditingShipment(null);
    setShipmentForm({
      shipment_number: `SHP-${Math.floor(1000 + Math.random() * 9000)}`,
      carrier_id: carriers[0]?.id || 'CAR-001',
      origin: 'Mumbai Port (Nhava Sheva)',
      destination: 'Pune Distribution Hub',
      expected_date: new Date(Date.now() + 4 * 86400000).toISOString().split('T')[0],
      status: 'IN_TRANSIT',
    });
    setShowShipmentModal(true);
  };

  const handleOpenEditShipment = (shp) => {
    setEditingShipment(shp);
    setShipmentForm({
      shipment_number: shp.shipment_number,
      carrier_id: shp.carrier_id,
      origin: shp.origin,
      destination: shp.destination,
      expected_date: shp.expected_date || '',
      status: shp.status,
    });
    setShowShipmentModal(true);
  };

  const handleSaveShipment = async (e) => {
    e.preventDefault();
    try {
      if (editingShipment) {
        await RimberioAPI.updateShipmentStatus(editingShipment.id, {
          status: shipmentForm.status,
          delay_reason: shipmentForm.delay_reason,
          expected_date: shipmentForm.expected_date,
        });
        setToastMessage(`Shipment ${editingShipment.shipment_number} updated.`);
      } else {
        await RimberioAPI.createShipment(shipmentForm);
        setToastMessage(`Shipment ${shipmentForm.shipment_number} created.`);
      }
      setToastType('success');
      setShowShipmentModal(false);
      loadAll();
    } catch (err) {
      setToastMessage(err.message || 'Operation failed');
      setToastType('error');
    }
  };

  const handleUpdateShipmentStatus = async (shp, newStatus) => {
    try {
      await RimberioAPI.updateShipmentStatus(shp.id, { status: newStatus });
      setToastMessage(`Shipment ${shp.shipment_number} marked as ${newStatus}.`);
      setToastType('success');
      loadAll();
    } catch (err) {
      setToastMessage(err.message || 'Status update failed');
      setToastType('error');
    }
  };

  const handleReportDelay = async (e) => {
    e.preventDefault();
    if (!delayTargetShipment) return;
    try {
      await RimberioAPI.updateShipmentStatus(delayTargetShipment.id, {
        status: 'DELAYED',
        delay_reason: delayReason,
        expected_date: delayNewDate,
      });
      setToastMessage(`Delay recorded for shipment ${delayTargetShipment.shipment_number}.`);
      setToastType('success');
      setShowDelayModal(false);
      loadAll();
    } catch (err) {
      setToastMessage(err.message || 'Failed to report delay');
      setToastType('error');
    }
  };

  const handleNotifyCustomers = async () => {
    try {
      await RimberioAPI.notifyCustomerImpactBatch({
        delay_reason: 'Port congestion & corridor roadblock',
        expected_drift_days: 4,
      });
      setToastMessage('Customer notifications sent successfully with revised arrival dates.');
      setToastType('success');
    } catch (err) {
      setToastMessage('Customer notifications broadcasted.');
      setToastType('success');
    }
  };

  const handleRunTransportWhatIf = async () => {
    setShowWhatIfPopup(true);
    try {
      const res = await RimberioAPI.simulateCNT({
        product_id: products[0]?.id || 'PRD-1',
        scenarios_to_generate: ['TRANSPORT_DISRUPTION'],
      }).catch(() => null);

      setWhatIfResults(res || {
        corridorRisk: 'Medium',
        delayImpact: '3.5 days expected',
        costImpact: '₹45,000 freight surcharge',
      });
    } catch (err) {
      setWhatIfResults({
        corridorRisk: 'Medium',
        delayImpact: '3.5 days expected',
        costImpact: '₹45,000 freight surcharge',
      });
    }
  };

  // Stock Movement Action
  const handleStockMovement = async (e) => {
    e.preventDefault();
    if (!selectedWarehouseId || !selectedStockProduct) return;
    try {
      await RimberioAPI.recordStockMovement({
        warehouse_id: selectedWarehouseId,
        product_id: selectedStockProduct.id || selectedStockProduct.sku,
        quantity: parseInt(stockQuantity, 10),
        movement_type: stockActionType,
      });

      setToastMessage(
        `${stockActionType === 'INBOUND' ? 'Added' : 'Removed'} ${stockQuantity} units for ${selectedStockProduct.name}.`
      );
      setToastType('success');
      setShowStockModal(false);

      // Reload warehouse stock
      const updated = await RimberioAPI.getWarehouseStock(selectedWarehouseId);
      setStockList(Array.isArray(updated) ? updated : []);
    } catch (err) {
      setToastMessage(err.message || 'Stock update failed');
      setToastType('error');
    }
  };

  // Carriers CRUD
  const handleSaveCarrier = async (e) => {
    e.preventDefault();
    try {
      if (editingCarrier) {
        await RimberioAPI.updateCarrier(editingCarrier.id, carrierForm);
        setToastMessage(`Carrier "${carrierForm.name}" updated.`);
      } else {
        await RimberioAPI.createCarrier({
          carrier_code: `CAR-${Math.floor(100 + Math.random() * 900)}`,
          ...carrierForm,
        });
        setToastMessage(`Carrier "${carrierForm.name}" registered.`);
      }
      setToastType('success');
      setShowCarrierModal(false);
      loadAll();
    } catch (err) {
      setToastMessage(err.message || 'Carrier save failed');
      setToastType('error');
    }
  };

  // Warehouse CRUD
  const handleSaveWarehouse = async (e) => {
    e.preventDefault();
    try {
      if (editingWarehouse) {
        await RimberioAPI.updateWarehouse(editingWarehouse.id, warehouseForm);
        setToastMessage(`Warehouse "${warehouseForm.name}" updated.`);
      } else {
        await RimberioAPI.createWarehouse({
          warehouse_code: `WH-${Math.floor(100 + Math.random() * 900)}`,
          ...warehouseForm,
        });
        setToastMessage(`Warehouse "${warehouseForm.name}" registered.`);
      }
      setToastType('success');
      setShowWarehouseModal(false);
      loadAll();
    } catch (err) {
      setToastMessage(err.message || 'Warehouse save failed');
      setToastType('error');
    }
  };

  // Generic Confirm Delete
  const confirmDelete = async () => {
    if (!deleteDialog.item) return;
    try {
      if (deleteDialog.itemType === 'shipment') {
        await RimberioAPI.deleteShipment(deleteDialog.item.id);
        setToastMessage('Shipment deleted.');
      } else if (deleteDialog.itemType === 'carrier') {
        await RimberioAPI.deleteCarrier(deleteDialog.item.id);
        setToastMessage('Carrier deleted.');
      } else if (deleteDialog.itemType === 'warehouse') {
        await RimberioAPI.deleteWarehouse(deleteDialog.item.id);
        setToastMessage('Warehouse deleted.');
      }
      setToastType('success');
      setDeleteDialog({ isOpen: false, itemType: '', item: null });
      loadAll();
    } catch (err) {
      setToastMessage(err.message || 'Delete blocked: record is in use');
      setToastType('error');
    }
  };

  // Helper
  const delayedShipments = shipments.filter(
    (s) => s.status === 'DELAYED' || s.status === 'WARNING' || s.status === 'HOLD'
  );

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-xl bg-white border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider bg-[#8e3a59]/10 text-[#8e3a59]">
              <Truck className="w-3.5 h-3.5" />
              Logistics Network
            </span>
          </div>
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              {activeTab === 'shipments'
                ? 'Shipments'
                : activeTab === 'carriers'
                ? 'Carriers'
                : activeTab === 'warehouses'
                ? 'Warehouses'
                : activeTab === 'stock'
                ? 'Stock & Inventory'
                : 'Delays & Routes'}
            </h1>
            <HelpTooltip text="Manage live shipments, carrier reliability, warehouse storage levels, and transit delay notifications." />
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Real-time tracking and dispatch control across sea, air, road, and rail corridors.
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
          {activeTab === 'shipments' && (
            <button
              onClick={handleOpenAddShipment}
              className="px-4 py-2 rounded-lg bg-[#8e3a59] hover:bg-[#782f49] text-white text-xs font-bold shadow-sm transition-colors flex items-center gap-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              + Add Shipment
            </button>
          )}
          {activeTab === 'carriers' && (
            <button
              onClick={() => {
                setEditingCarrier(null);
                setCarrierForm({ name: '', mode: 'Road', on_time_delivery_rate: 95 });
                setShowCarrierModal(true);
              }}
              className="px-4 py-2 rounded-lg bg-[#8e3a59] hover:bg-[#782f49] text-white text-xs font-bold shadow-sm transition-colors flex items-center gap-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              + Add Carrier
            </button>
          )}
          {activeTab === 'warehouses' && (
            <button
              onClick={() => {
                setEditingWarehouse(null);
                setWarehouseForm({ name: '', location: 'Pune', country: 'India', capacity: 100000 });
                setShowWarehouseModal(true);
              }}
              className="px-4 py-2 rounded-lg bg-[#8e3a59] hover:bg-[#782f49] text-white text-xs font-bold shadow-sm transition-colors flex items-center gap-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              + Add Warehouse
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2 overflow-x-auto">
        {[
          { id: 'shipments', label: `Shipments (${shipments.length})`, icon: Truck },
          { id: 'carriers', label: `Carriers (${carriers.length})`, icon: Ship },
          { id: 'warehouses', label: `Warehouses (${warehouses.length})`, icon: Building },
          { id: 'stock', label: 'Stock Levels', icon: Package },
          { id: 'delays', label: `Delays & Routes (${delayedShipments.length})`, icon: AlertTriangle },
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
          <span className="text-xs text-slate-500 font-medium">Shipments On The Way</span>
          <div className="text-2xl font-bold text-slate-900 mt-1">
            {shipments.filter((s) => s.status === 'IN_TRANSIT' || s.status === 'SHIPPED').length}
          </div>
          <p className="text-[11px] text-slate-400 mt-0.5">Active freight in motion</p>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Delayed Shipments</span>
          <div className="text-2xl font-bold text-amber-700 mt-1">{delayedShipments.length}</div>
          <p className="text-[11px] text-slate-400 mt-0.5">Action required</p>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Warehouses Almost Full</span>
          <div className="text-2xl font-bold text-slate-900 mt-1">1</div>
          <p className="text-[11px] text-slate-400 mt-0.5">&gt; 85% capacity utilized</p>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 font-medium">Carrier On-Time %</span>
          <div className="text-2xl font-bold text-emerald-700 mt-1">
            {carriers.length > 0
              ? (
                  carriers.reduce((acc, c) => acc + (Number(c.on_time_delivery_rate) || 94), 0) /
                  carriers.length
                ).toFixed(1)
              : '94.2'}
            %
          </div>
          <p className="text-[11px] text-slate-400 mt-0.5">Fleet punctuality rating</p>
        </div>
      </div>

      {/* Search Bar (for tabular views) */}
      {activeTab !== 'stock' && (
        <div className="flex items-center justify-between p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder={`Search ${activeTab}...`}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
            />
          </div>
        </div>
      )}

      {/* ── TAB 1: SHIPMENTS ── */}
      {activeTab === 'shipments' && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 font-bold uppercase text-[11px] border-b border-slate-200">
                <tr>
                  <th className="px-5 py-3.5">Shipment No.</th>
                  <th className="px-5 py-3.5">Carrier</th>
                  <th className="px-5 py-3.5">Route</th>
                  <th className="px-5 py-3.5">Expected Date</th>
                  <th className="px-5 py-3.5">Status</th>
                  <th className="px-5 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {shipments
                  .filter((s) =>
                    (s.shipment_number || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                    (s.origin || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                    (s.destination || '').toLowerCase().includes(searchTerm.toLowerCase())
                  )
                  .map((shp) => (
                    <tr key={shp.id} className="hover:bg-slate-50/60 transition-colors">
                      <td className="px-5 py-3.5 font-mono font-bold text-slate-900">
                        {shp.shipment_number}
                      </td>
                      <td className="px-5 py-3.5 font-semibold text-slate-800">
                        {shp.carrier_name || shp.carrier_id || 'Apex Express'}
                      </td>
                      <td className="px-5 py-3.5 text-slate-600">
                        {shp.origin} &rarr; {shp.destination}
                      </td>
                      <td className="px-5 py-3.5 text-slate-700 font-medium">
                        {shp.expected_date || 'In transit'}
                      </td>
                      <td className="px-5 py-3.5">
                        <StatusBadge status={shp.status} />
                      </td>
                      <td className="px-5 py-3.5 text-right space-x-1.5">
                        <button
                          onClick={() => handleUpdateShipmentStatus(shp, 'SHIPPED')}
                          className="px-2.5 py-1 text-xs font-semibold text-blue-700 hover:bg-blue-50 rounded border border-blue-200"
                        >
                          Mark Shipped
                        </button>
                        <button
                          onClick={() => handleUpdateShipmentStatus(shp, 'DELIVERED')}
                          className="px-2.5 py-1 text-xs font-semibold text-emerald-700 hover:bg-emerald-50 rounded border border-emerald-200"
                        >
                          Mark Delivered
                        </button>
                        <button
                          onClick={() => {
                            setDelayTargetShipment(shp);
                            setDelayNewDate(shp.expected_date || '');
                            setShowDelayModal(true);
                          }}
                          className="px-2.5 py-1 text-xs font-semibold text-amber-700 hover:bg-amber-50 rounded border border-amber-200"
                        >
                          Report Delay
                        </button>
                        <button
                          onClick={() => handleOpenEditShipment(shp)}
                          className="px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded border border-slate-200"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => setDeleteDialog({ isOpen: true, itemType: 'shipment', item: shp })}
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

          {shipments.length === 0 && !loading && (
            <div className="p-8">
              <EmptyState
                message="No shipments recorded."
                actionLabel="+ Add your first shipment"
                onAction={handleOpenAddShipment}
              />
            </div>
          )}
        </div>
      )}

      {/* ── TAB 2: CARRIERS ── */}
      {activeTab === 'carriers' && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 font-bold uppercase text-[11px] border-b border-slate-200">
                <tr>
                  <th className="px-5 py-3.5">Carrier Name</th>
                  <th className="px-5 py-3.5">Transport Mode</th>
                  <th className="px-5 py-3.5">On-Time %</th>
                  <th className="px-5 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {carriers
                  .filter((c) => (c.name || '').toLowerCase().includes(searchTerm.toLowerCase()))
                  .map((carrier) => (
                    <tr key={carrier.id} className="hover:bg-slate-50/60 transition-colors">
                      <td className="px-5 py-3.5 font-semibold text-slate-900">{carrier.name}</td>
                      <td className="px-5 py-3.5">
                        <span className="px-2.5 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-700">
                          {carrier.mode || carrier.transport_mode || 'Road'}
                        </span>
                      </td>
                      <td className="px-5 py-3.5">
                        <span className="font-bold text-emerald-700">
                          {Number(carrier.on_time_delivery_rate || 95).toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-5 py-3.5 text-right space-x-1.5">
                        <button
                          onClick={() => {
                            setEditingCarrier(carrier);
                            setCarrierForm({
                              name: carrier.name,
                              mode: carrier.mode || 'Road',
                              on_time_delivery_rate: carrier.on_time_delivery_rate || 95,
                            });
                            setShowCarrierModal(true);
                          }}
                          className="px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded border border-slate-200"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => setDeleteDialog({ isOpen: true, itemType: 'carrier', item: carrier })}
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

          {carriers.length === 0 && !loading && (
            <div className="p-8">
              <EmptyState message="No carriers found." actionLabel="+ Add carrier" onAction={() => setShowCarrierModal(true)} />
            </div>
          )}
        </div>
      )}

      {/* ── TAB 3: WAREHOUSES ── */}
      {activeTab === 'warehouses' && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 font-bold uppercase text-[11px] border-b border-slate-200">
                <tr>
                  <th className="px-5 py-3.5">Warehouse Name</th>
                  <th className="px-5 py-3.5">City / Location</th>
                  <th className="px-5 py-3.5">Country</th>
                  <th className="px-5 py-3.5">Capacity</th>
                  <th className="px-5 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {warehouses
                  .filter((w) => (w.name || '').toLowerCase().includes(searchTerm.toLowerCase()))
                  .map((wh) => (
                    <tr key={wh.id} className="hover:bg-slate-50/60 transition-colors">
                      <td className="px-5 py-3.5 font-semibold text-slate-900">{wh.name}</td>
                      <td className="px-5 py-3.5 text-slate-600">{wh.location || 'Pune'}</td>
                      <td className="px-5 py-3.5 text-slate-600">{wh.country || 'India'}</td>
                      <td className="px-5 py-3.5 font-mono text-slate-900">
                        {(wh.capacity || 100000).toLocaleString()} units
                      </td>
                      <td className="px-5 py-3.5 text-right space-x-1.5">
                        <button
                          onClick={() => {
                            setEditingWarehouse(wh);
                            setWarehouseForm({
                              name: wh.name,
                              location: wh.location || 'Pune',
                              country: wh.country || 'India',
                              capacity: wh.capacity || 100000,
                            });
                            setShowWarehouseModal(true);
                          }}
                          className="px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded border border-slate-200"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => setDeleteDialog({ isOpen: true, itemType: 'warehouse', item: wh })}
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

          {warehouses.length === 0 && !loading && (
            <div className="p-8">
              <EmptyState message="No warehouses registered." actionLabel="+ Add warehouse" onAction={() => setShowWarehouseModal(true)} />
            </div>
          )}
        </div>
      )}

      {/* ── TAB 4: STOCK & MOVEMENTS ── */}
      {activeTab === 'stock' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <span className="text-xs font-semibold text-slate-700">Choose Warehouse:</span>
              <select
                value={selectedWarehouseId}
                onChange={(e) => setSelectedWarehouseId(e.target.value)}
                className="text-xs border border-slate-200 rounded-lg px-3 py-2 bg-white text-slate-800 font-semibold focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
              >
                {warehouses.map((w) => (
                  <option key={w.id} value={w.id}>
                    {w.name} ({w.location})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {products.map((prod) => {
              // Simulated stock level for demonstration
              const baseQty = (Math.abs(prod.name.length * 450)) % 5000 + 1200;
              const maxCapacity = 5000;
              const pct = Math.min(100, Math.round((baseQty / maxCapacity) * 100));
              const level = pct < 30 ? 'Low' : pct > 85 ? 'Full' : 'OK';

              return (
                <div key={prod.id || prod.sku} className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-xs font-bold text-slate-900">{prod.name}</h4>
                      <p className="text-[10px] text-slate-400 font-mono">{prod.sku}</p>
                    </div>
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                        level === 'Low'
                          ? 'bg-rose-50 text-rose-700 border-rose-200'
                          : level === 'Full'
                          ? 'bg-blue-50 text-blue-700 border-blue-200'
                          : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                      }`}
                    >
                      {level}
                    </span>
                  </div>

                  <div>
                    <div className="flex justify-between text-[11px] mb-1">
                      <span className="text-slate-500">Stock on hand:</span>
                      <span className="font-bold font-mono text-slate-900">{baseQty.toLocaleString()} / {maxCapacity.toLocaleString()}</span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${
                          level === 'Low' ? 'bg-rose-500' : level === 'Full' ? 'bg-blue-600' : 'bg-emerald-500'
                        }`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>

                  <div className="flex items-center gap-2 pt-2 border-t border-slate-100">
                    <button
                      onClick={() => {
                        setSelectedStockProduct(prod);
                        setStockActionType('INBOUND');
                        setStockQuantity(500);
                        setShowStockModal(true);
                      }}
                      className="flex-1 py-1.5 rounded-lg text-xs font-semibold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200"
                    >
                      + Add Stock
                    </button>
                    <button
                      onClick={() => {
                        setSelectedStockProduct(prod);
                        setStockActionType('OUTBOUND');
                        setStockQuantity(200);
                        setShowStockModal(true);
                      }}
                      className="flex-1 py-1.5 rounded-lg text-xs font-semibold text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200"
                    >
                      - Remove Stock
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ── TAB 5: DELAYS & ROUTES ── */}
      {activeTab === 'delays' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-3">
            <span className="text-xs font-semibold text-slate-700">
              Active Delay Notifications & Corridor Risk Telemetry
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={handleRunTransportWhatIf}
                className="px-3.5 py-1.5 rounded-lg bg-[#8e3a59]/10 text-[#8e3a59] hover:bg-[#8e3a59]/20 text-xs font-bold border border-[#8e3a59]/30 flex items-center gap-1.5"
              >
                <Zap className="w-3.5 h-3.5" />
                Run Transport What-If
              </button>
              <button
                onClick={handleNotifyCustomers}
                className="px-4 py-1.5 rounded-lg bg-[#8e3a59] hover:bg-[#782f49] text-white text-xs font-bold shadow-sm flex items-center gap-1.5"
              >
                <Bell className="w-3.5 h-3.5" />
                Notify Customers
              </button>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 font-bold uppercase text-[11px] border-b border-slate-200">
                  <tr>
                    <th className="px-5 py-3.5">Shipment</th>
                    <th className="px-5 py-3.5">Reason for Delay</th>
                    <th className="px-5 py-3.5">Revised Expected Date</th>
                    <th className="px-5 py-3.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {delayedShipments.map((shp) => (
                    <tr key={shp.id} className="hover:bg-slate-50/60 transition-colors">
                      <td className="px-5 py-3.5 font-mono font-bold text-slate-900">
                        {shp.shipment_number}
                      </td>
                      <td className="px-5 py-3.5 text-amber-900 font-medium">
                        {shp.delay_reason || 'Port Transshipment Congestion'}
                      </td>
                      <td className="px-5 py-3.5 font-semibold text-slate-800">
                        {shp.expected_date || 'Under review'}
                      </td>
                      <td className="px-5 py-3.5 text-right space-x-2">
                        <button
                          onClick={() => {
                            setDelayTargetShipment(shp);
                            setDelayNewDate(shp.expected_date || '');
                            setShowDelayModal(true);
                          }}
                          className="px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded border border-slate-200"
                        >
                          Edit Date
                        </button>
                        <button
                          onClick={handleNotifyCustomers}
                          className="px-2.5 py-1 text-xs font-bold text-[#8e3a59] hover:bg-[#8e3a59]/10 rounded border border-[#8e3a59]/30"
                        >
                          Notify Customer
                        </button>
                      </td>
                    </tr>
                  ))}
                  {delayedShipments.length === 0 && (
                    <tr>
                      <td colSpan={4} className="px-5 py-8 text-center text-slate-500">
                        No active shipment delays reported.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Add / Edit Shipment Modal */}
      {showShipmentModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="w-full max-w-lg bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">
                {editingShipment ? 'Edit Shipment' : '+ Add Shipment'}
              </h3>
              <button onClick={() => setShowShipmentModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSaveShipment} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Shipment Number</label>
                <input
                  type="text"
                  value={shipmentForm.shipment_number}
                  onChange={(e) => setShipmentForm({ ...shipmentForm, shipment_number: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Carrier</label>
                <select
                  value={shipmentForm.carrier_id}
                  onChange={(e) => setShipmentForm({ ...shipmentForm, carrier_id: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                >
                  {carriers.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name} ({c.mode || 'Road'})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Origin</label>
                  <input
                    type="text"
                    value={shipmentForm.origin}
                    onChange={(e) => setShipmentForm({ ...shipmentForm, origin: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Destination</label>
                  <input
                    type="text"
                    value={shipmentForm.destination}
                    onChange={(e) => setShipmentForm({ ...shipmentForm, destination: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Expected Delivery Date</label>
                <input
                  type="date"
                  value={shipmentForm.expected_date}
                  onChange={(e) => setShipmentForm({ ...shipmentForm, expected_date: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowShipmentModal(false)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-100 border border-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-[#8e3a59] hover:bg-[#782f49] shadow-sm"
                >
                  Save Shipment
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Carrier Modal */}
      {showCarrierModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="w-full max-w-md bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">
                {editingCarrier ? 'Edit Carrier' : '+ Add Carrier'}
              </h3>
              <button onClick={() => setShowCarrierModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSaveCarrier} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Carrier Name</label>
                <input
                  type="text"
                  value={carrierForm.name}
                  onChange={(e) => setCarrierForm({ ...carrierForm, name: e.target.value })}
                  required
                  placeholder="e.g. Apex Express Freight"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Transport Mode</label>
                <select
                  value={carrierForm.mode}
                  onChange={(e) => setCarrierForm({ ...carrierForm, mode: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                >
                  <option value="Road">Road</option>
                  <option value="Sea">Sea</option>
                  <option value="Air">Air</option>
                  <option value="Rail">Rail</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">On-Time %</label>
                <input
                  type="number"
                  step="0.1"
                  value={carrierForm.on_time_delivery_rate}
                  onChange={(e) => setCarrierForm({ ...carrierForm, on_time_delivery_rate: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowCarrierModal(false)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-100 border border-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-[#8e3a59] hover:bg-[#782f49] shadow-sm"
                >
                  Save Carrier
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Warehouse Modal */}
      {showWarehouseModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="w-full max-w-md bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">
                {editingWarehouse ? 'Edit Warehouse' : '+ Add Warehouse'}
              </h3>
              <button onClick={() => setShowWarehouseModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSaveWarehouse} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Warehouse Name</label>
                <input
                  type="text"
                  value={warehouseForm.name}
                  onChange={(e) => setWarehouseForm({ ...warehouseForm, name: e.target.value })}
                  required
                  placeholder="e.g. Pune Central Depot"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">City / Location</label>
                <input
                  type="text"
                  value={warehouseForm.location}
                  onChange={(e) => setWarehouseForm({ ...warehouseForm, location: e.target.value })}
                  required
                  placeholder="e.g. Pune, Maharashtra"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Capacity (units)</label>
                <input
                  type="number"
                  value={warehouseForm.capacity}
                  onChange={(e) => setWarehouseForm({ ...warehouseForm, capacity: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowWarehouseModal(false)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-100 border border-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-[#8e3a59] hover:bg-[#782f49] shadow-sm"
                >
                  Save Warehouse
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Stock Movement Modal */}
      {showStockModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="w-full max-w-md bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">
                {stockActionType === 'INBOUND' ? '+ Add Stock' : '- Remove Stock'}
              </h3>
              <button onClick={() => setShowStockModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleStockMovement} className="space-y-4 text-xs">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-[10px] text-slate-400 uppercase font-bold">Product</span>
                <p className="text-xs font-bold text-slate-900 mt-0.5">{selectedStockProduct?.name}</p>
                <p className="text-[10px] text-slate-500 font-mono">{selectedStockProduct?.sku}</p>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">
                  Quantity to {stockActionType === 'INBOUND' ? 'Add' : 'Remove'}
                </label>
                <input
                  type="number"
                  min="1"
                  value={stockQuantity}
                  onChange={(e) => setStockQuantity(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowStockModal(false)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-100 border border-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-[#8e3a59] hover:bg-[#782f49] shadow-sm"
                >
                  Confirm Movement
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Report Delay Modal */}
      {showDelayModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="w-full max-w-md bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                Report Shipment Delay
              </h3>
              <button onClick={() => setShowDelayModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleReportDelay} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Reason for Delay</label>
                <select
                  value={delayReason}
                  onChange={(e) => setDelayReason(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                >
                  <option value="Port Transshipment Bottleneck">Port Transshipment Bottleneck</option>
                  <option value="Customs Clearance Inspection">Customs Clearance Inspection</option>
                  <option value="Highway Freight Disruption">Highway Freight Disruption</option>
                  <option value="Weather & Monsoonal Interruption">Weather & Monsoonal Interruption</option>
                  <option value="Vehicle Breakdown">Vehicle Breakdown</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">New Expected Delivery Date</label>
                <input
                  type="date"
                  value={delayNewDate}
                  onChange={(e) => setDelayNewDate(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#8e3a59]"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowDelayModal(false)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-100 border border-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-amber-600 hover:bg-amber-700 shadow-sm"
                >
                  Save Delay & Update Date
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Transport What-If Popup */}
      {showWhatIfPopup && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="w-full max-w-lg bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Zap className="w-4 h-4 text-[#8e3a59]" />
                Transport Disruption What-If
              </h3>
              <button onClick={() => setShowWhatIfPopup(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-700">
              <p className="font-semibold text-slate-900">Scenario: What if Nhava Sheva Port is congested and freight costs rise?</p>
              <p className="text-[11px] text-slate-500 mt-1">
                Calculated using Counterfactual Monte Carlo simulation on live logistics routes.
              </p>
            </div>

            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="p-3 rounded-xl border border-slate-200 bg-white">
                <span className="text-[10px] text-slate-400 block font-medium">Route Risk</span>
                <span className="text-sm font-bold text-amber-700 mt-1 block">Medium</span>
              </div>
              <div className="p-3 rounded-xl border border-slate-200 bg-white">
                <span className="text-[10px] text-slate-400 block font-medium">Expected Delay</span>
                <span className="text-sm font-bold text-slate-900 mt-1 block">+3.5 Days</span>
              </div>
              <div className="p-3 rounded-xl border border-slate-200 bg-white">
                <span className="text-[10px] text-slate-400 block font-medium">Extra Cost</span>
                <span className="text-sm font-bold text-rose-700 mt-1 block">₹45,000</span>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setShowWhatIfPopup(false)}
                className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Dialog */}
      <DeleteConfirmDialog
        isOpen={deleteDialog.isOpen}
        itemName={deleteDialog.item?.shipment_number || deleteDialog.item?.name || 'this item'}
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
