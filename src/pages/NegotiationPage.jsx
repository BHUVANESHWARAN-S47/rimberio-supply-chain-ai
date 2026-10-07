import React, { useState } from 'react';
import { Bot, CheckCircle2, Send, Pause, Play } from 'lucide-react';

export const NegotiationPage = () => {
  const [buyerTarget, setBuyerTarget] = useState(142.5);
  const [supplierOffer, setSupplierOffer] = useState(148.2);
  const [leadTime, setLeadTime] = useState(12);
  const [isSimulating, setIsSimulating] = useState(true);

  const [logs, setLogs] = useState([
    {
      round: 1,
      sender: 'BUYER_AI',
      message:
        'Initiated micro-negotiation for 10,000 units SKU #MK-902. Proposed baseline: $140.00/unit, 10-day SLA.',
      time: '10:00:14 AM',
    },
    {
      round: 1,
      sender: 'SUPPLIER_AI',
      message: 'Rejected baseline. Air freight surcharge requires $158.00/unit with 14-day SLA.',
      time: '10:00:22 AM',
    },
    {
      round: 2,
      sender: 'BUYER_AI',
      message: 'Counter-offer: $145.00/unit with dual-carrier penalty clause (0.5%/day delay).',
      time: '10:01:05 AM',
    },
    {
      round: 3,
      sender: 'SUPPLIER_AI',
      message: 'Accepted penalty clause on condition of 12-day SLA window. Counter: $150.00/unit.',
      time: '10:01:48 AM',
    },
    {
      round: 4,
      sender: 'BUYER_AI',
      message:
        'Autonomous solver optimized target: $148.20/unit, 12-day SLA. Presenting for acceptance.',
      time: '10:02:15 AM',
    },
  ]);

  const handleStep = () => {
    const n = (supplierOffer - 1.2).toFixed(2);
    setSupplierOffer(parseFloat(n));
    setLogs((prev) => [
      ...prev,
      {
        round: prev.length + 1,
        sender: 'SUPPLIER_AI',
        message: `Concession round #${prev.length + 1}: Adjusted unit price to $${n} with guaranteed 12-day delivery window.`,
        time: new Date().toLocaleTimeString(),
      },
    ]);
  };

  return (
    <div className="space-y-5 pb-12">
      {/* Banner */}
      <div
        className="p-5 rounded-[6px] flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-[#d9dad3]"
      >
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="badge badge-teal">MULTI-AGENT CONSOLE</span>
            <span className="rim-mono text-xs text-[#5c5c5c]">
              • VENDOR: Semiconductor Direct Corp
            </span>
          </div>
          <h1 className="text-xl md:text-2xl font-bold text-black" style={{ letterSpacing: '-0.02em', color: '#000000' }}>
            AI NEGOTIATION CONSOLE
          </h1>
          <p className="text-xs text-[#5c5c5c] mt-0.5">
            Autonomous AI agent negotiating optimal spot-market terms using game-theoretic utility functions.
          </p>
        </div>
        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setIsSimulating(!isSimulating)}
            className="rim-btn-secondary"
            style={{ padding: '8px 16px', fontSize: '12px' }}
          >
            {isSimulating ? (
              <Pause className="w-3.5 h-3.5 text-black" />
            ) : (
              <Play className="w-3.5 h-3.5 text-black" />
            )}
            {isSimulating ? 'Agent Active' : 'Resume Agent'}
          </button>
          <button
            onClick={handleStep}
            className="rim-btn-primary"
            style={{ padding: '8px 18px', fontSize: '12px' }}
          >
            <Bot className="w-4 h-4 text-black" /> Force Next Concession
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left: Parameters */}
        <div className="lg:col-span-4 p-5 rounded-[6px] space-y-4 bg-white border border-[#d9dad3]">
          <div className="p-3.5 rounded-[6px] border border-[#d9dad3] bg-[#edede8]">
            <div className="flex justify-between text-xs mb-2.5">
              <span
                className="font-bold uppercase tracking-wider text-[#5c5c5c]"
                style={{ fontSize: '0.6875rem' }}
              >
                AGREEMENT METRICS
              </span>
              <span className="badge badge-healthy">94.8% OPTIMAL</span>
            </div>
            <div className="space-y-1.5 text-xs">
              {[
                ['Target Unit Price', `$${buyerTarget.toFixed(2)}`, '#000000'],
                ['Supplier Offer', `$${supplierOffer.toFixed(2)}`, '#000000'],
                ['SLA Lead Time', `${leadTime} Days`, '#000000'],
                ['Projected Savings', '$98,000', '#000000'],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between">
                  <span className="text-[#5c5c5c] font-medium">{k}:</span>
                  <span className="font-bold rim-mono text-black">{v}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-3.5">
            <h3 className="rim-section-title text-black font-bold">Negotiation Parameters</h3>
            {[
              {
                label: 'Target Unit Price ($)',
                val: buyerTarget,
                min: 130,
                max: 160,
                step: 0.5,
                set: setBuyerTarget,
                display: `$${buyerTarget}`,
              },
              {
                label: 'Max Lead Time (Days)',
                val: leadTime,
                min: 7,
                max: 21,
                step: 1,
                set: setLeadTime,
                display: `${leadTime} Days`,
              },
            ].map(({ label, val, min, max, step, set, display }) => (
              <div key={label} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold text-black">
                  <span className="text-[#303030]">{label}</span>
                  <span className="rim-mono font-bold text-black">{display}</span>
                </div>
                <input
                  type="range"
                  min={min}
                  max={max}
                  step={step}
                  value={val}
                  onChange={(e) => set(parseFloat(e.target.value))}
                  className="w-full cursor-pointer accent-black h-1 bg-[#edede8] rounded-[2px]"
                />
              </div>
            ))}
          </div>

          <button
            onClick={() => alert(`Contract executed at $${supplierOffer.toFixed(2)}/unit!`)}
            className="rim-btn-primary w-full"
            style={{ padding: '10px 16px', fontSize: '13px' }}
          >
            <CheckCircle2 className="w-4 h-4 text-black" /> Execute Autonomous Agreement
          </button>
        </div>

        {/* Right: Terminal (Hairline drafting table) */}
        <div
          className="lg:col-span-8 p-5 rounded-[6px] flex flex-col justify-between bg-white border border-[#d9dad3]"
          style={{ height: '480px' }}
        >
          <div className="flex items-center justify-between pb-3 border-b border-[#d9dad3] mb-3">
            <div className="flex items-center gap-2">
              <Bot className="w-4 h-4 text-black" />
              <h2
                className="text-xs font-bold uppercase tracking-wider text-black"
                style={{ color: '#000000' }}
              >
                LIVE AGENT NEGOTIATION TERMINAL
              </h2>
            </div>
            <span className="rim-mono text-[10px] text-[#5c5c5c]">
              ENCRYPTED · STITCH MCP
            </span>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2.5 pr-2 pb-2">
            {logs.map((item, i) => (
              <div
                key={i}
                className={`p-3 rounded-[6px] text-xs space-y-1 ${item.sender === 'BUYER_AI' ? 'ml-6' : 'mr-6'}`}
                style={{
                  background: item.sender === 'BUYER_AI' ? '#fae8ff' : '#ffffff',
                  border: item.sender === 'BUYER_AI' ? '1px solid #f0abfc' : '1px solid #d9dad3',
                }}
              >
                <div className="flex justify-between items-center rim-mono text-[10px]">
                  <span className="font-bold text-black">
                    {item.sender === 'BUYER_AI'
                      ? '🤖 RIMBERIO BUYER AGENT'
                      : '🏢 SUPPLIER AI AGENT'}
                  </span>
                  <span className="text-[#5c5c5c]">{item.time}</span>
                </div>
                <p className="text-black" style={{ color: '#000000' }}>
                  {item.message}
                </p>
              </div>
            ))}
          </div>

          <div className="pt-3 flex items-center gap-2 border-t border-[#d9dad3]">
            <input
              type="text"
              placeholder="Inject manual directive to Buyer Agent..."
              className="rim-input flex-1 text-xs py-2 text-black"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && e.currentTarget.value) {
                  const val = e.currentTarget.value;
                  setLogs((prev) => [
                    ...prev,
                    {
                      round: prev.length + 1,
                      sender: 'BUYER_AI',
                      message: `[OVERRIDE]: ${val}`,
                      time: new Date().toLocaleTimeString(),
                    },
                  ]);
                  e.currentTarget.value = '';
                }
              }}
            />
            <button onClick={handleStep} className="rim-btn-primary p-2">
              <Send className="w-4 h-4 text-black" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
