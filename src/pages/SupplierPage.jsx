import React, { useState } from 'react';
import { Building2, Star, Users, MapPin } from 'lucide-react';

export const SupplierPage = () => {
  const [activeFilter, setActiveFilter] = useState('ALL');

  const suppliers = [
    {
      id: 'SUP-001',
      name: 'Semiconductor Direct Corp',
      tier: 'T1',
      region: 'Taiwan / Hsinchu',
      category: 'Micro-Capacitors',
      status: 'WARNING',
      sla: 89.2,
      risk: 42,
      delivery: 14,
      spend: '$1,240,000',
      esc: 'A-',
    },
    {
      id: 'SUP-002',
      name: 'Apex Global Logistics Ltd',
      tier: 'T1',
      region: 'Singapore / Jurong',
      category: 'Power Management ICs',
      status: 'HEALTHY',
      sla: 98.4,
      risk: 12,
      delivery: 10,
      spend: '$980,000',
      esc: 'AAA',
    },
    {
      id: 'SUP-003',
      name: 'Yokohama Precision Components',
      tier: 'T2',
      region: 'Japan / Kanagawa',
      category: 'Resistors & Crystals',
      status: 'HEALTHY',
      sla: 96.1,
      risk: 18,
      delivery: 12,
      spend: '$640,000',
      esc: 'AA',
    },
    {
      id: 'SUP-004',
      name: 'Hamburg Silicon Fabrication GmbH',
      tier: 'T1',
      region: 'Germany / Hamburg',
      category: 'MEMS Sensors',
      status: 'CRITICAL',
      sla: 74.8,
      risk: 78,
      delivery: 22,
      spend: '$2,100,000',
      esc: 'BBB',
    },
    {
      id: 'SUP-005',
      name: 'Shenzhen PCB Manufacturing',
      tier: 'T2',
      region: 'China / Guangdong',
      category: 'PCB Assemblies',
      status: 'WARNING',
      sla: 88.6,
      risk: 44,
      delivery: 15,
      spend: '$450,000',
      esc: 'A',
    },
    {
      id: 'SUP-006',
      name: 'Nordic Semiconductor Solutions',
      tier: 'T1',
      region: 'Norway / Trondheim',
      category: 'BLE Microcontrollers',
      status: 'HEALTHY',
      sla: 97.9,
      risk: 14,
      delivery: 9,
      spend: '$1,850,000',
      esc: 'AAA',
    },
  ];

  const filters = ['ALL', 'HEALTHY', 'WARNING', 'CRITICAL', 'T1', 'T2'];

  const filtered =
    activeFilter === 'ALL'
      ? suppliers
      : suppliers.filter((s) => s.status === activeFilter || s.tier === activeFilter);

  const statusStyle = {
    HEALTHY: { badge: 'badge-healthy', bar: '#176537' },
    WARNING: { badge: 'badge-brand', bar: '#bb899b' },
    CRITICAL: { badge: 'badge-critical', bar: '#8c2323' },
  };

  return (
    <div className="space-y-5 pb-12">
      <div
        className="p-5 rounded-[6px] flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-[#d9dad3]"
      >
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="badge badge-healthy">ESG CERTIFIED</span>
            <span className="rim-mono text-xs text-[#5c5c5c]">
              • 504 vendors tracked
            </span>
          </div>
          <h1 className="text-xl md:text-2xl font-bold text-black" style={{ letterSpacing: '-0.02em', color: '#000000' }}>
            SUPPLIER INTELLIGENCE WORKSPACE
          </h1>
          <p className="text-xs text-[#5c5c5c] mt-0.5">
            Multi-criteria SLA scorecards, ESG ratings, financial exposure, and Tier mapping.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="p-3.5 rounded-[6px] text-center bg-[#edede8] border border-[#d9dad3] min-w-[90px]">
            <p className="text-xl font-bold rim-mono text-black" style={{ color: '#000000' }}>
              504
            </p>
            <p className="rim-section-title text-[9px] text-[#5c5c5c] font-bold">Total Vendors</p>
          </div>
          <div className="p-3.5 rounded-[6px] text-center bg-[#fae8ff] border border-[#f0abfc] min-w-[90px]">
            <p className="text-xl font-bold rim-mono text-[#a21caf]">11</p>
            <p className="rim-section-title text-[9px] text-[#a21caf] font-bold">At Risk</p>
          </div>
        </div>
      </div>

      <div className="rounded-[6px] overflow-hidden bg-white border border-[#d9dad3]">
        {/* Filters */}
        <div className="px-4 py-2.5 flex items-center gap-2 flex-wrap border-b border-[#d9dad3] bg-[#edede8]">
          <Users className="w-4 h-4 text-black mr-1" />
          {filters.map((f) => (
            <button
              key={f}
              onClick={() => setActiveFilter(f)}
              className="px-3 py-1 rounded-[6px] text-xs font-semibold tracking-wider transition-all"
              style={{
                background: activeFilter === f ? '#000000' : '#ffffff',
                color: activeFilter === f ? 'white' : '#000000',
                border: activeFilter === f ? '1px solid #000000' : '1px solid #d9dad3',
                fontSize: '0.6875rem',
              }}
            >
              {f}
            </button>
          ))}
        </div>

        {/* Table */}
        <table className="w-full">
          <thead>
            <tr>
              {[
                'Supplier',
                'Tier / Region',
                'Category',
                'Status',
                'SLA Score',
                'Risk Index',
                'Avg Delivery',
                'YTD Spend',
                'ESG',
              ].map((col) => (
                <th
                  key={col}
                  className="rim-th text-left font-bold text-black"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((s) => {
              const ss = statusStyle[s.status];
              return (
                <tr key={s.id} className="rim-tr cursor-pointer">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2.5">
                      <div className="w-7 h-7 rounded-[4px] flex items-center justify-center shrink-0 bg-[#edede8] border border-[#d9dad3]">
                        <Building2 className="w-3.5 h-3.5 text-black" />
                      </div>
                      <div>
                        <p className="text-xs font-bold text-black" style={{ color: '#000000' }}>
                          {s.name}
                        </p>
                        <p className="rim-mono text-[10px] text-[#5c5c5c]">
                          {s.id}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <p className="text-xs font-semibold text-black">
                      TIER {s.tier.slice(1)}
                    </p>
                    <div className="flex items-center gap-1 text-[10px] text-[#5c5c5c]">
                      <MapPin className="w-3 h-3 text-[#5c5c5c]" /> {s.region}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-xs text-[#303030]">
                    {s.category}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`badge ${ss.badge}`}>{s.status}</span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 rounded-[2px] bg-[#d9dad3]">
                        <div
                          className="h-1.5 rounded-[2px]"
                          style={{ width: `${s.sla}%`, background: ss.bar }}
                        />
                      </div>
                      <span className="rim-mono text-xs font-bold text-black">
                        {s.sla}%
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 rim-mono text-xs font-bold text-black">
                    {s.risk}/100
                  </td>
                  <td className="px-4 py-3 text-xs text-black">
                    {s.delivery} Days
                  </td>
                  <td className="px-4 py-3 rim-mono text-xs font-bold text-black">
                    {s.spend}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <Star className="w-3 h-3 text-black fill-black" />
                      <span className="rim-mono text-xs font-bold text-black">
                        {s.esc}
                      </span>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
