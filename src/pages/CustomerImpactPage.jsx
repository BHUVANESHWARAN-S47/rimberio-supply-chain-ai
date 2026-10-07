import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import {
  Send,
  CheckCircle,
  Clock,
  RefreshCw,
  BellRing,
} from 'lucide-react';

export const CustomerImpactPage = () => {
  const { customerNoticesCount, setCustomerNoticesCount, setNotification } = useApp();

  const [orders, setOrders] = useState([
    {
      id: 'ORD-8941',
      client: 'Boeing Commercial Aviation',
      sku: 'Titanium Structural Fasteners (Lot #990)',
      originalSupplier: 'Pacific Component Corp',
      switchedSupplier: 'Apex Global Logistics',
      originalETA: 'Oct 14, 2026',
      revisedETA: 'Oct 17, 2026 (+3 Days)',
      slaStatus: 'COMPLIANT_WITH_NOTICE',
      slaImpact: 'Low Risk',
      status: 'SENT',
      contact: 'procurement@boeing.com',
      units: '2,400 Units',
    },
    {
      id: 'ORD-8942',
      client: 'Tesla Energy Division',
      sku: 'Micro-Capacitor Array #772',
      originalSupplier: 'Pacific Component Corp',
      switchedSupplier: 'Apex Global Logistics',
      originalETA: 'Oct 12, 2026',
      revisedETA: 'Oct 16, 2026 (+4 Days)',
      slaStatus: 'BUFFERED',
      slaImpact: 'Medium Risk',
      status: 'PENDING',
      contact: 'supply-cell@tesla.com',
      units: '18,500 Units',
    },
    {
      id: 'ORD-8945',
      client: 'Siemens Healthineers',
      sku: 'Precision Sensor Bus Module B4',
      originalSupplier: 'Nordic Precision AG',
      switchedSupplier: 'Nexus Logistics Hub',
      originalETA: 'Oct 18, 2026',
      revisedETA: 'Oct 20, 2026 (+2 Days)',
      slaStatus: 'COMPLIANT',
      slaImpact: 'Minimal',
      status: 'PENDING',
      contact: 'logistics@siemens-health.com',
      units: '650 Units',
    },
    {
      id: 'ORD-8949',
      client: 'Foxconn Industrial Internet',
      sku: 'SMD Power Resistor Packs',
      originalSupplier: 'Pacific Component Corp',
      switchedSupplier: 'Apex Global Logistics',
      originalETA: 'Oct 15, 2026',
      revisedETA: 'Oct 19, 2026 (+4 Days)',
      slaStatus: 'BUFFERED',
      slaImpact: 'Medium Risk',
      status: 'PENDING',
      contact: 'operations@foxconn-global.com',
      units: '40,000 Units',
    },
    {
      id: 'ORD-8954',
      client: 'ABB Robotics International',
      sku: 'Servo Control Arm Assemblies',
      originalSupplier: 'Vanguard Freightways',
      switchedSupplier: 'Apex Global Logistics',
      originalETA: 'Oct 21, 2026',
      revisedETA: 'Oct 22, 2026 (+1 Day)',
      slaStatus: 'COMPLIANT',
      slaImpact: 'Minimal',
      status: 'SENT',
      contact: 'supply@abb.com',
      units: '120 Units',
    },
  ]);

  const [selectedOrder, setSelectedOrder] = useState(orders[1]);
  const [dispatching, setDispatching] = useState(false);
  const [filter, setFilter] = useState('ALL');

  const handleSendSingle = (orderId) => {
    setOrders((prev) => prev.map((o) => (o.id === orderId ? { ...o, status: 'SENT' } : o)));
    setCustomerNoticesCount((c) => c + 1);
    setNotification({
      show: true,
      message: `Customer transparency notice dispatched for order ${orderId} with updated delivery schedule.`,
    });
  };

  const handleSendBatch = async () => {
    setDispatching(true);
    await new Promise((r) => setTimeout(r, 700));
    setOrders((prev) => prev.map((o) => ({ ...o, status: 'SENT' })));
    setCustomerNoticesCount((c) => c + 3);
    setDispatching(false);
    setNotification({
      show: true,
      message:
        'Batch Customer Notifications Dispatched: 5 enterprise accounts updated with full transparency.',
    });
  };

  const filteredOrders = orders.filter((o) => {
    if (filter === 'PENDING') return o.status === 'PENDING';
    if (filter === 'SENT') return o.status === 'SENT';
    return true;
  });

  return (
    <div className="space-y-5 pb-12">
      {/* ── HEADER ── */}
      <div className="p-5 rounded-[6px] flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-[#d9dad3]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="badge badge-teal">PIPELINE STEPS 7 & 8</span>
            <span className="badge badge-healthy">CUSTOMER-AWARE TWIN</span>
          </div>
          <h1
            className="text-xl md:text-2xl font-bold uppercase text-black"
            style={{ letterSpacing: '-0.02em', color: '#000000' }}
          >
            CUSTOMER IMPACT & NOTIFICATION ENGINE
          </h1>
          <p className="text-xs text-[#5c5c5c] mt-0.5">
            Downstream transparency layer: Assess SLA impacts of supplier switching and dispatch automated schedule revisions.
          </p>
        </div>

        <button
          onClick={handleSendBatch}
          disabled={dispatching}
          className="rim-btn-primary shrink-0"
          style={{ padding: '8px 18px', fontSize: '13px' }}
        >
          {dispatching ? (
            <RefreshCw className="w-4 h-4 animate-spin text-black" />
          ) : (
            <Send className="w-4 h-4 text-black" />
          )}
          <span>{dispatching ? 'Dispatching Batch...' : 'Dispatch All Pending Notices'}</span>
        </button>
      </div>

      {/* ── METRIC STATS BANNER ── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'AFFECTED ACCOUNTS', val: '5 Clients', sub: 'Across 61,670 Total Units' },
          { label: 'AVG TRANSIT DELTA', val: '+2.8 Days', sub: 'Buffered within safety stock' },
          { label: 'SLA ADHERENCE', val: '98.6%', sub: 'Penalty waived via early notice' },
          { label: 'NOTICES DISPATCHED', val: `${customerNoticesCount} Notices`, sub: '100% Client transparency' },
        ].map((m) => (
          <div key={m.label} className="p-4 rounded-[6px] bg-white border border-[#d9dad3]">
            <p className="text-[10px] font-bold uppercase tracking-wider text-[#5c5c5c]">
              {m.label}
            </p>
            <p className="text-xl font-bold rim-mono text-black mt-1">{m.val}</p>
            <p className="text-[11px] text-[#5c5c5c] mt-0.5">{m.sub}</p>
          </div>
        ))}
      </div>

      {/* ── TWO-COLUMN WORKSPACE: ORDERS TABLE & LIVE ADVISORY PREVIEW ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left: Orders Impact Table */}
        <div className="lg:col-span-7 p-5 rounded-[6px] bg-white border border-[#d9dad3] space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#d9dad3]">
            <div>
              <h2 className="text-xs font-bold uppercase tracking-wider text-black">
                Affected Enterprise Client Orders
              </h2>
              <p className="text-xs text-[#5c5c5c]">
                Orders impacted by switching from incumbent to candidate supplier
              </p>
            </div>
            <div className="flex gap-1 bg-[#edede8] p-1 rounded-[6px]">
              {['ALL', 'PENDING', 'SENT'].map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className="text-[10px] font-bold uppercase px-2.5 py-1 rounded-[4px] transition-colors"
                  style={{
                    background: filter === f ? '#000000' : 'transparent',
                    color: filter === f ? '#FFFFFF' : '#000000',
                  }}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            {filteredOrders.map((ord) => {
              const isSelected = selectedOrder.id === ord.id;
              return (
                <div
                  key={ord.id}
                  onClick={() => setSelectedOrder(ord)}
                  className="p-3.5 rounded-[6px] border transition-all cursor-pointer"
                  style={{
                    borderColor: isSelected ? 'var(--color-palette-1)' : 'var(--color-stone)',
                    background: isSelected ? 'var(--color-palette-5)' : '#ffffff',
                    borderWidth: isSelected ? '2px' : '1px',
                  }}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="rim-mono text-xs font-bold text-black">{ord.id}</span>
                        <span className="font-semibold text-xs text-black">· {ord.client}</span>
                      </div>
                      <p className="text-xs text-[#5c5c5c] mt-0.5">{ord.sku}</p>
                    </div>

                    <span
                      className={`badge shrink-0 ${
                        ord.status === 'SENT' ? 'badge-healthy' : 'badge-teal'
                      }`}
                    >
                      {ord.status === 'SENT' ? 'NOTICE SENT' : 'PENDING'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-[11px] font-semibold text-black mt-2 pt-2 border-t border-[#d9dad3]">
                    <div className="flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-[#5c5c5c]" />
                      <span>Revised ETA: {ord.revisedETA}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[#5c5c5c]">{ord.units}</span>
                      {ord.status === 'PENDING' && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleSendSingle(ord.id);
                          }}
                          className="px-2 py-0.5 rounded-[4px] bg-black text-white text-[10px] font-bold hover:bg-black/80"
                        >
                          Send Notice
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Live Advisory Preview */}
        <div className="lg:col-span-5 p-5 rounded-[6px] bg-white border border-[#d9dad3] flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#d9dad3]">
              <div className="flex items-center gap-2">
                <BellRing className="w-4 h-4 text-black" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-black">
                  TRANSPARENCY NOTICE DISPATCH
                </h3>
              </div>
              <span className="badge badge-teal">TEMPLATED ADVISORY</span>
            </div>

            {/* Email Payload (Drafting table bone surface) */}
            <div
              className="p-3.5 rounded-[6px] text-xs space-y-2.5 bg-[#edede8] border border-[#d9dad3]"
            >
              <div className="flex items-center justify-between border-b border-[#d9dad3] pb-2">
                <div>
                  <p className="text-[10px] font-bold uppercase text-[#5c5c5c]">RECIPIENT</p>
                  <p className="font-semibold text-black">{selectedOrder.contact}</p>
                </div>
                <div className="text-right">
                  <p className="text-[10px] font-bold uppercase text-[#5c5c5c]">ACCOUNT</p>
                  <p className="font-semibold text-black">{selectedOrder.client}</p>
                </div>
              </div>

              <div>
                <p className="text-[10px] font-bold uppercase text-[#5c5c5c] mb-0.5">SUBJECT</p>
                <p className="font-bold text-xs text-black">
                  RIMBERIO NOTICE: Schedule Optimization & Supplier Switch — Order {selectedOrder.id}
                </p>
              </div>

              <div className="p-3 bg-white rounded-[4px] border border-[#d9dad3] space-y-2 text-black">
                <p className="font-semibold text-[11px] leading-relaxed">
                  Dear Supply Chain Director at {selectedOrder.client},
                </p>
                <p className="leading-relaxed text-[11px] text-[#303030]">
                  Under our proactive SLA monitoring protocols, RIMBERIO AI has initiated a controlled supplier transition for{' '}
                  <span className="font-bold text-black">{selectedOrder.sku}</span> from{' '}
                  <span className="underline">{selectedOrder.originalSupplier}</span> to{' '}
                  <span className="underline font-bold text-black">{selectedOrder.switchedSupplier}</span> to prevent maritime bottlenecks.
                </p>
                <div className="p-2 rounded-[4px] bg-[#edede8] text-[10px] space-y-1">
                  <div className="flex justify-between">
                    <span className="text-[#5c5c5c]">Original ETA:</span>
                    <span>{selectedOrder.originalETA}</span>
                  </div>
                  <div className="flex justify-between font-bold">
                    <span>Revised Guaranteed ETA:</span>
                    <span>{selectedOrder.revisedETA}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#5c5c5c]">Quality Assurance Level:</span>
                    <span className="text-[#0d5432] font-bold">100% Mil-Spec Certified</span>
                  </div>
                </div>
                <p className="text-[10px] text-[#5c5c5c] leading-normal">
                  No action is required from your team. Real-time GPS tracking and container telemetry remain accessible via your RIMBERIO client portal.
                </p>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-[#d9dad3] mt-3">
            <button
              onClick={() => handleSendSingle(selectedOrder.id)}
              disabled={selectedOrder.status === 'SENT'}
              className="w-full rim-btn-primary"
              style={{
                background: selectedOrder.status === 'SENT' ? '#edede8' : 'var(--color-primary-magenta)',
                border: selectedOrder.status === 'SENT' ? '1px solid #d9dad3' : '1px solid rgba(0,0,0,0.1)',
                color: selectedOrder.status === 'SENT' ? '#5c5c5c' : '#ffffff',
                cursor: selectedOrder.status === 'SENT' ? 'not-allowed' : 'pointer',
              }}
            >
              {selectedOrder.status === 'SENT' ? (
                <>
                  <CheckCircle className="w-4 h-4 text-[#0d5432]" /> Notice Already Dispatched
                </>
              ) : (
                <>
                  <Send className="w-4 h-4 text-white" /> Dispatch Notice to {selectedOrder.client}
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
