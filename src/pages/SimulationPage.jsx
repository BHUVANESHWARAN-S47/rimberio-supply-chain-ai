import React, { useState } from 'react';
import { Sliders, ShieldAlert, ArrowRight, DollarSign, Clock } from 'lucide-react';
import { useApp } from '../context/AppContext';

export const SimulationPage = () => {
  const { setCurrentPage } = useApp();
  const [suezDays, setSuezDays] = useState(6);
  const [freightSurge, setFreightSurge] = useState(25);
  const [demandSurge, setDemandSurge] = useState(15);
  const [vendorFail, setVendorFail] = useState(false);

  const costImpact = Math.round(
    180000 + suezDays * 28000 + freightSurge * 4200 + (vendorFail ? 150000 : 0)
  );
  const slaRisk = Math.min(99, Math.round(12 + suezDays * 4.5 + (vendorFail ? 35 : 0)));

  return (
    <div className="space-y-5 pb-12">
      {/* Top Banner (Drafting Table 6px Card) */}
      <div
        className="p-5 rounded-[6px] flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-[#d9dad3]"
      >
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="badge badge-teal">PREDICTIVE PLAYGROUND</span>
            <span className="rim-mono text-xs text-[#5c5c5c]">
              • SCENARIO #09
            </span>
          </div>
          <h1 className="text-xl md:text-2xl font-bold text-black" style={{ letterSpacing: '-0.02em', color: '#000000' }}>
            COUNTERFACTUAL TWIN SIMULATION
          </h1>
          <p className="text-xs text-[#5c5c5c] mt-0.5">
            Simulate macro supply chain shocks and evaluate autonomous mitigation strategies before deployment.
          </p>
        </div>
        <button
          onClick={() => setCurrentPage('decision_center')}
          className="rim-btn-primary shrink-0"
          style={{ padding: '8px 18px', fontSize: '13px' }}
        >
          Apply Recommended Mitigation <ArrowRight className="w-4 h-4 text-black" />
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Controls */}
        <div className="lg:col-span-5 p-5 rounded-[6px] space-y-4 bg-white border border-[#d9dad3]">
          <div className="flex items-center gap-2 pb-3 border-b border-[#d9dad3]">
            <Sliders className="w-4 h-4 text-black" />
            <h2
              className="text-xs font-bold uppercase tracking-wider text-black"
              style={{ color: '#000000' }}
            >
              DISRUPTION PARAMETER CONTROLS
            </h2>
          </div>

          {[
            {
              label: 'Maritime Delay (Suez / Panama)',
              val: suezDays,
              min: 0,
              max: 20,
              set: setSuezDays,
              unit: 'Days',
            },
            {
              label: 'Air & Sea Freight Rate Surge (%)',
              val: freightSurge,
              min: 0,
              max: 100,
              set: setFreightSurge,
              unit: '%',
            },
            {
              label: 'Regional Demand Surge (%)',
              val: demandSurge,
              min: 0,
              max: 50,
              set: setDemandSurge,
              unit: '%',
            },
          ].map(({ label, val, min, max, set, unit }) => (
            <div key={label} className="space-y-1.5">
              <div className="flex justify-between text-xs font-semibold text-black">
                <span className="text-[#303030]">{label}</span>
                <span className="rim-mono font-bold text-black">
                  +{val}
                  {unit}
                </span>
              </div>
              <input
                type="range"
                min={min}
                max={max}
                value={val}
                onChange={(e) => set(parseInt(e.target.value))}
                className="w-full cursor-pointer accent-black h-1 bg-[#edede8] rounded-[2px]"
              />
            </div>
          ))}

          <div className="p-3.5 rounded-[6px] flex items-center justify-between border border-[#d9dad3] bg-[#edede8]">
            <div>
              <p className="text-xs font-bold text-black" style={{ color: '#000000' }}>
                Tier-1 Supplier Failure Simulation
              </p>
              <p className="text-[11px] text-[#5c5c5c] mt-0.5">
                Simulate total shutdown of primary foundry.
              </p>
            </div>
            <input
              type="checkbox"
              checked={vendorFail}
              onChange={(e) => setVendorFail(e.target.checked)}
              className="w-4 h-4 rounded-[4px] accent-black"
            />
          </div>
        </div>

        {/* Impact */}
        <div className="lg:col-span-7 p-5 rounded-[6px] space-y-4 bg-white border border-[#d9dad3]">
          <div className="flex items-center justify-between pb-3 border-b border-[#d9dad3]">
            <h2
              className="text-xs font-bold uppercase tracking-wider flex items-center gap-2 text-black"
              style={{ color: '#000000' }}
            >
              <ShieldAlert className="w-4 h-4 text-black" /> SIMULATED IMPACT PROJECTION
            </h2>
            <span className="badge badge-healthy">TWIN CONFIDENCE: 98.2%</span>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div
              className="p-4 rounded-[6px] bg-[#edede8] border border-[#d9dad3]"
            >
              <div className="flex justify-between text-xs mb-2">
                <span
                  className="font-bold uppercase tracking-wider text-[#5c5c5c]"
                  style={{ fontSize: '0.6875rem' }}
                >
                  COST IMPACT
                </span>
                <DollarSign className="w-4 h-4 text-black" />
              </div>
              <p className="text-2xl font-bold rim-mono text-black">
                ${costImpact.toLocaleString()}
              </p>
              <p className="text-xs mt-1 text-[#5c5c5c]">Surcharges + buffer holding</p>
            </div>
            <div
              className="p-4 rounded-[6px] bg-[#fae8ff] border border-[#f0abfc]"
            >
              <div className="flex justify-between text-xs mb-2">
                <span
                  className="font-bold uppercase tracking-wider text-black"
                  style={{ fontSize: '0.6875rem' }}
                >
                  SLA RISK
                </span>
                <Clock className="w-4 h-4 text-black" />
              </div>
              <p className="text-2xl font-bold rim-mono text-black">{slaRisk}%</p>
              <p className="text-xs mt-1 text-[#5c5c5c]">Probability of breach</p>
            </div>
          </div>

          <div className="p-4 rounded-[6px] border border-[#d9dad3] bg-[#edede8]">
            <h3 className="rim-section-title text-[9px] mb-2 text-black font-bold">
              AUTONOMOUS MITIGATION RECOMMENDATION
            </h3>
            <div className="space-y-2 text-xs">
              <div className="flex items-start gap-2">
                <ArrowRight className="w-4 h-4 shrink-0 mt-0.5 text-black" />
                <p className="text-black" style={{ color: '#000000' }}>
                  <strong className="font-bold text-black">Option A (Optimal):</strong> Reroute 60% via Hamburg Rail + dispatch AI spot negotiation.{' '}
                  <span className="rim-mono font-bold text-black">
                    +$42K cost → Saves $210K
                  </span>
                </p>
              </div>
              <div className="flex items-start gap-2">
                <ArrowRight className="w-4 h-4 shrink-0 mt-0.5 text-black" />
                <p className="text-black" style={{ color: '#000000' }}>
                  <strong className="font-bold text-black">Option B (Air Expedite):</strong> Shift 100% to chartered air freight.{' '}
                  <span className="rim-mono text-[#5c5c5c]">
                    +$190K, 0 days SLA delay
                  </span>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
