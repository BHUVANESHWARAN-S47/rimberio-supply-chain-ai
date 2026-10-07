import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { Zap, Compass, Plane, Truck, CheckCircle, ChevronRight } from 'lucide-react';

export const DecisionCenterPage = () => {
  const { activeDisruption } = useApp();
  const [applied, setApplied] = useState(null);

  const options = [
    {
      id: 'A',
      label: 'RAIL EXPEDITE + SPOT NEGOTIATION',
      icon: Compass,
      bg: '#fae8ff',
      border: '#f0abfc',
      desc: 'Reroute 60% of volume via Hamburg-Rotterdam rail corridor and dispatch micro-negotiation agents to secure spot-market capacity.',
      cost: '+$42,000',
      delay: '+1.5 Days',
      savings: 'Saves $210,000 vs baseline',
      confidence: 98.2,
    },
    {
      id: 'B',
      label: 'AIR FREIGHT CHARTER',
      icon: Plane,
      bg: '#edede8',
      border: '#d9dad3',
      desc: 'Expedite 100% of critical SKUs via chartered air cargo through Frankfurt hub.',
      cost: '+$190,000',
      delay: '0 Days',
      savings: 'Zero delay SLA',
      confidence: 96.0,
    },
    {
      id: 'C',
      label: 'DUAL SUPPLIER FAILOVER',
      icon: Truck,
      bg: '#ffffff',
      border: '#d9dad3',
      desc: 'Activate secondary Tier-2 suppliers (Yokohama) for partial fulfillment while primary route clears.',
      cost: '+$68,000',
      delay: '+4 Days',
      savings: 'Saves $120,000',
      confidence: 88.7,
    },
  ];

  return (
    <div className="space-y-5 pb-12">
      <div
        className="p-5 rounded-[6px] flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-[#d9dad3]"
      >
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="badge badge-teal">AUTONOMOUS DECISION ENGINE</span>
            <span className="rim-mono text-xs text-[#5c5c5c]">
              • Disruption: {activeDisruption?.id || 'DIS-2026-089'}
            </span>
          </div>
          <h1 className="text-xl md:text-2xl font-bold text-black" style={{ letterSpacing: '-0.02em', color: '#000000' }}>
            ADAPTIVE DECISION CENTER
          </h1>
          <p className="text-xs text-[#5c5c5c] mt-0.5">
            AI-generated mitigation playbook ranked by cost-efficiency, SLA preservation, and agent confidence.
          </p>
        </div>
        <div className="p-3.5 rounded-[6px] text-center bg-[#edede8] border border-[#d9dad3] min-w-[110px]">
          <div className="flex items-center justify-center gap-1.5 mb-0.5">
            <Zap className="w-4 h-4 text-black" />
            <span className="text-lg font-bold rim-mono text-black">
              98.2%
            </span>
          </div>
          <p className="rim-section-title text-[9px] text-[#5c5c5c] font-bold">Model Confidence</p>
        </div>
      </div>

      {applied && (
        <div
          className="p-4 rounded-[6px] flex items-center gap-3 bg-[#eafbf2] border border-[#b2e8c9]"
        >
          <CheckCircle className="w-5 h-5 text-[#0d5432] shrink-0" />
          <div>
            <h3 className="font-bold text-xs text-[#0d5432]">
              Mitigation Option {applied} Applied Successfully
            </h3>
            <p className="text-[11px] text-[#0d5432] mt-0.5">
              AI agents dispatched. Warehouse hub operators notified. ETA update pushed to RIMBERIO Control Tower.
            </p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4">
        {options.map((opt) => {
          const Icon = opt.icon;
          return (
            <div
              key={opt.id}
              className="p-5 rounded-[6px] flex flex-col md:flex-row md:items-center justify-between gap-5 bg-white border transition-colors hover:border-black"
              style={{
                borderColor: applied === opt.id ? '#000000' : '#d9dad3',
                borderWidth: applied === opt.id ? '2px' : '1px',
              }}
            >
              <div className="flex items-start gap-3.5 flex-1">
                <div
                  className="w-10 h-10 rounded-[6px] flex items-center justify-center shrink-0"
                  style={{ background: opt.bg, border: `1px solid ${opt.border}` }}
                >
                  <Icon className="w-5 h-5 text-black" />
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h3
                      className="text-xs font-bold uppercase tracking-wider text-black"
                      style={{ color: '#000000' }}
                    >
                      OPTION {opt.id}: {opt.label}
                    </h3>
                    {opt.id === 'A' && <span className="badge badge-teal">RECOMMENDED</span>}
                  </div>
                  <p className="text-xs text-[#303030] mb-2 font-normal">
                    {opt.desc}
                  </p>
                  <div className="flex items-center gap-3 text-xs">
                    <span className="rim-mono text-[#5c5c5c]">
                      Cost: <strong className="text-black">{opt.cost}</strong>
                    </span>
                    <span className="rim-mono text-[#5c5c5c]">
                      Delay: <strong className="text-black">{opt.delay}</strong>
                    </span>
                    <span className="badge badge-healthy">{opt.savings}</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3 shrink-0">
                <div className="text-center min-w-[70px]">
                  <p className="text-lg font-bold rim-mono text-black">
                    {opt.confidence}%
                  </p>
                  <p className="rim-section-title text-[9px] text-[#5c5c5c] font-bold">
                    Confidence
                  </p>
                </div>
                <button
                  onClick={() => setApplied(opt.id)}
                  className="rim-btn-primary"
                  style={{ padding: '8px 16px', fontSize: '12px' }}
                >
                  Apply Option {opt.id} <ChevronRight className="w-3.5 h-3.5 text-black" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
