import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import {
  Activity,
  AlertTriangle,
  Bot,
  Globe,
  Sliders,
  Zap,
  Clock,
  DollarSign,
  PackageCheck,
  ChevronRight,
  Navigation,
  Info,
  Radio,
  Anchor,
  Train,
  Factory,
} from 'lucide-react';

export const DashboardPage = () => {
  const { setCurrentPage, activeDisruption } = useApp();
  const [selectedNodeId, setSelectedNodeId] = useState('suez');

  const nodes = [
    {
      id: 'shanghai',
      name: 'Shanghai Marine Hub & Foundry',
      category: 'Semiconductor Origin Hub',
      country: 'East Asia',
      status: 'NORMAL',
      delay: '+0.2 Days (Nominal)',
      skus: 3420,
      vessels: 14,
      latency: '45ms',
      coords: { top: '38%', left: '78%' },
      icon: Factory,
      action: 'High-yield micro-capacitor production running on schedule. Standard maritime booking.',
      agent: 'Buyer Agent (Monitoring Batch #772)',
    },
    {
      id: 'singapore',
      name: 'Singapore Straits Transshipment',
      category: 'Maritime Anchorage Hub',
      country: 'Southeast Asia',
      status: 'WARNING',
      delay: '+1.8 Days (Berth Queue)',
      skus: 1950,
      vessels: 9,
      latency: '82ms',
      coords: { top: '56%', left: '74%' },
      icon: Anchor,
      action: 'Minor port congestion; feeder vessels delayed by 36 hours. Priority container staging enabled.',
      agent: 'Logistics Agent (Transit Rescheduling)',
    },
    {
      id: 'suez',
      name: 'Suez Canal Maritime Chokepoint',
      category: 'Critical Canal Bottleneck',
      country: 'Red Sea / Egypt',
      status: 'DISRUPTED',
      delay: '+4.2 Days (Severe Queuing)',
      skus: 2180,
      vessels: 22,
      latency: '145ms',
      coords: { top: '42%', left: '56%' },
      icon: AlertTriangle,
      action: 'High vessel backlog causing cascading delays. Autonomous switching policy recommends Cape route or Apex Global foundry.',
      agent: 'Admin Auditor Agent (Triggering Vendor Switch)',
    },
    {
      id: 'rotterdam',
      name: 'Rotterdam Port Gateway',
      category: 'European Deepwater Seaport',
      country: 'Netherlands / EU',
      status: 'NORMAL',
      delay: '0.0 Days (On Schedule)',
      skus: 4120,
      vessels: 18,
      latency: '35ms',
      coords: { top: '28%', left: '49%' },
      icon: Anchor,
      action: 'Automated crane terminals operational. Rail transfer to Rhine corridor synchronized.',
      agent: 'Customer Impact Agent (SLA Monitoring)',
    },
    {
      id: 'hamburg',
      name: 'Hamburg Intermodal Railhead',
      category: 'Central Rail Distribution',
      country: 'Germany',
      status: 'NORMAL',
      delay: '+0.4 Days (Nominal)',
      skus: 2820,
      vessels: 6,
      latency: '30ms',
      coords: { top: '25%', left: '52%' },
      icon: Train,
      action: 'Cross-docking buffer inventory healthy. Tier-1 customer fulfillment on track.',
      agent: 'Inventory Balancing Agent',
    },
    {
      id: 'los_angeles',
      name: 'Los Angeles / Long Beach Gateway',
      category: 'US West Coast Marine Terminal',
      country: 'United States',
      status: 'NORMAL',
      delay: '+0.8 Days (Normal Gate Turn)',
      skus: 3800,
      vessels: 12,
      latency: '52ms',
      coords: { top: '38%', left: '19%' },
      icon: Anchor,
      action: 'Trans-Pacific inbound vessels cleared. Alameda corridor rail connections active.',
      agent: 'Logistics Agent (Tracking Intermodal Turn)',
    },
    {
      id: 'chicago',
      name: 'Chicago Inland Rail Hub',
      category: 'Midwest Distribution Center',
      country: 'United States',
      status: 'NORMAL',
      delay: '0.0 Days (Nominal)',
      skus: 2650,
      vessels: 4,
      latency: '38ms',
      coords: { top: '33%', left: '26%' },
      icon: Train,
      action: 'Central assembly stock buffers stable. Zero SLA breach risk detected.',
      agent: 'Customer Impact Agent',
    },
  ];

  const activeNode = nodes.find((n) => n.id === selectedNodeId) || nodes[0];

  const getNodeColor = (status) => {
    switch (status) {
      case 'DISRUPTED':
        return '#ef4444'; // Red
      case 'WARNING':
        return '#f59e0b'; // Amber
      case 'NORMAL':
      default:
        return '#10b981'; // Emerald
    }
  };

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      {/* ── Page Header ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-lg bg-white border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider bg-slate-100 text-slate-800 border border-slate-200">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              Live Digital Twin Telemetry
            </span>
            <span className="font-mono text-xs text-slate-500">
              • 2026-10-07 Real-Time Feed
            </span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Global Supply Chain Intelligence Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Real-time multi-agent telemetry, maritime route delays, and autonomous buyer-supplier negotiations.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setCurrentPage('simulation')}
            className="px-4 py-2 rounded-md border border-slate-300 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 transition-colors flex items-center gap-1.5"
          >
            <Sliders className="w-3.5 h-3.5 text-slate-600" />
            Counterfactual Sim
          </button>
          <button
            onClick={() => setCurrentPage('negotiation')}
            className="px-4 py-2 rounded-md bg-[#8e3a59] hover:bg-[#752d48] text-white text-xs font-semibold shadow-sm transition-all flex items-center gap-1.5"
          >
            <Bot className="w-4 h-4" />
            Launch AI Negotiation
          </button>
        </div>
      </div>

      {/* ── Disruption Alert ── */}
      {activeDisruption && (
        <div className="p-4 rounded-lg bg-amber-50 border border-amber-200 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="flex items-start gap-3.5">
            <div className="w-9 h-9 rounded-md bg-white border border-amber-300 flex items-center justify-center shrink-0">
              <AlertTriangle className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-0.5">
                <span className="font-mono text-xs font-bold text-amber-900">
                  {activeDisruption.id}
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-amber-200 text-amber-900">
                  Critical Disruption
                </span>
              </div>
              <h3 className="text-sm font-bold text-slate-900">
                {activeDisruption.title}
              </h3>
              <p className="text-xs text-slate-600 mt-0.5">
                Impact: <strong>{activeDisruption.impactedSKUs} SKUs</strong> · Financial Risk: <strong>{activeDisruption.estimatedCostImpact}</strong> · Delay: <strong>+{activeDisruption.delayDays} Days</strong>
              </p>
            </div>
          </div>
          <button
            onClick={() => setCurrentPage('decision_center')}
            className="px-4 py-2 rounded-md bg-[#8e3a59] hover:bg-[#752d48] text-white text-xs font-semibold shadow-sm transition-all shrink-0 flex items-center gap-1.5"
          >
            <Zap className="w-3.5 h-3.5" />
            Apply AI Mitigation Policy
          </button>
        </div>
      )}

      {/* ── KPI Cards ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            icon: PackageCheck,
            label: 'Total Active SKUs',
            value: '14,820',
            sub: '99.4% SLA Compliance',
            badgeBg: 'bg-emerald-50 text-emerald-700 border-emerald-200',
          },
          {
            icon: Bot,
            label: 'Autonomous Negotiations',
            value: '18 Rounds',
            sub: 'Active Multi-Agents',
            badgeBg: 'bg-purple-50 text-purple-700 border-purple-200',
          },
          {
            icon: DollarSign,
            label: 'Cost Savings Generated',
            value: '$412,800',
            sub: '+14.2% vs Baseline',
            badgeBg: 'bg-emerald-50 text-emerald-700 border-emerald-200',
          },
          {
            icon: Clock,
            label: 'Global Network Latency',
            value: '14.2 Days',
            sub: 'Suez Delay Factor',
            badgeBg: 'bg-slate-100 text-slate-700 border-slate-200',
          },
        ].map(({ icon: Icon, label, value, sub, badgeBg }) => (
          <div
            key={label}
            className="p-5 rounded-lg bg-white border border-slate-200 shadow-sm hover:border-slate-300 transition-colors"
          >
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                {label}
              </span>
              <Icon className="w-4 h-4 text-slate-400" />
            </div>
            <p className="text-2xl font-bold font-mono text-slate-900 tracking-tight">
              {value}
            </p>
            <div className="mt-2.5">
              <span className={`inline-block px-2 py-0.5 rounded text-[11px] font-medium border ${badgeBg}`}>
                {sub}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* ── PROPER GLOBAL DIGITAL TWIN NETWORK MAP ── */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6 space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-200 gap-3">
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Globe className="w-4 h-4 text-[#8e3a59]" />
              Global Digital Twin Network Map
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Real-time AIS vessel telemetry, global maritime chokepoints, and predicted transit delays
            </p>
          </div>

          <div className="flex items-center gap-4 text-xs font-medium">
            <span className="flex items-center gap-1.5 text-slate-700">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block shadow-sm"></span>
              Normal Transit
            </span>
            <span className="flex items-center gap-1.5 text-slate-700">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block shadow-sm"></span>
              Queue Warning
            </span>
            <span className="flex items-center gap-1.5 text-slate-700">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block shadow-sm animate-pulse"></span>
              Disrupted Bottleneck
            </span>
          </div>
        </div>

        {/* ── Map Canvas with Real SVG Continents & Animated Maritime Routes ── */}
        <div className="relative w-full h-[380px] sm:h-[440px] rounded-lg overflow-hidden bg-slate-950 border border-slate-800">
          {/* Subtle Grid Coordinates */}
          <div
            className="absolute inset-0 opacity-15 pointer-events-none"
            style={{
              backgroundImage: 'radial-gradient(circle, #94a3b8 1px, transparent 1px)',
              backgroundSize: '28px 28px',
            }}
          />

          {/* SVG Cartographic World Continents & Maritime Trade Lanes */}
          <svg className="absolute inset-0 w-full h-full" viewBox="0 0 1000 500" preserveAspectRatio="none">
            {/* World Landmass Silhouettes (Simplified Continent Outlines) */}
            <g fill="#1e293b" stroke="#334155" strokeWidth="1" opacity="0.8">
              {/* North America */}
              <path d="M 120 70 L 260 65 L 290 120 L 250 170 L 240 230 L 190 220 L 160 170 L 110 130 Z" />
              {/* South America */}
              <path d="M 230 240 L 290 270 L 270 380 L 220 440 L 200 370 L 210 270 Z" />
              {/* Europe */}
              <path d="M 460 70 L 550 65 L 560 140 L 480 160 L 450 110 Z" />
              {/* Africa */}
              <path d="M 460 170 L 570 170 L 590 270 L 540 390 L 480 370 L 450 250 Z" />
              {/* Asia */}
              <path d="M 570 70 L 890 80 L 870 230 L 780 270 L 680 240 L 600 160 Z" />
              {/* Australia */}
              <path d="M 780 330 L 880 340 L 870 430 L 790 420 Z" />
              {/* UK / Islands */}
              <path d="M 450 90 L 470 90 L 465 120 L 445 110 Z" />
              {/* Japan */}
              <path d="M 870 140 L 885 160 L 875 190 L 860 170 Z" />
            </g>

            {/* Maritime Corridor 1: Asia-Europe via Suez Canal (Shanghai -> Singapore -> Suez -> Rotterdam -> Hamburg) */}
            <path
              d="M 780 190 Q 750 260 740 280 T 560 210 T 490 140 T 520 125"
              fill="none"
              stroke="#ef4444"
              strokeWidth="2.5"
              strokeDasharray="6 4"
              opacity="0.8"
            />

            {/* Maritime Corridor 2: Trans-Pacific Express (Shanghai -> Los Angeles) */}
            <path
              d="M 780 190 Q 890 220 980 200"
              fill="none"
              stroke="#38bdf8"
              strokeWidth="2"
              strokeDasharray="5 4"
              opacity="0.6"
            />
            <path
              d="M 20 200 Q 100 200 190 190"
              fill="none"
              stroke="#38bdf8"
              strokeWidth="2"
              strokeDasharray="5 4"
              opacity="0.6"
            />

            {/* Rail Corridor 3: US Inland Rail (Los Angeles -> Chicago) */}
            <line
              x1="190"
              y1="190"
              x2="260"
              y2="165"
              stroke="#10b981"
              strokeWidth="2"
              strokeDasharray="4 3"
              opacity="0.8"
            />
          </svg>

          {/* ── Interactive Hub Markers on the Map ── */}
          {nodes.map((node) => {
            const isSelected = node.id === selectedNodeId;
            const markerColor = getNodeColor(node.status);

            return (
              <div
                key={node.id}
                onClick={() => setSelectedNodeId(node.id)}
                style={{ top: node.coords.top, left: node.coords.left }}
                className="absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer group z-20"
              >
                <div className="relative flex items-center justify-center">
                  {/* Ping Animation for Warnings/Disruptions */}
                  {node.status !== 'NORMAL' && (
                    <span
                      className="absolute w-6 h-6 rounded-full animate-ping opacity-75"
                      style={{ background: markerColor }}
                    />
                  )}

                  {/* Node Dot */}
                  <span
                    className={`w-4 h-4 rounded-full border-2 transition-transform duration-200 ${
                      isSelected ? 'scale-125 border-white ring-2 ring-white/50' : 'border-slate-900 group-hover:scale-110'
                    }`}
                    style={{ background: markerColor }}
                  />

                  {/* Node Tag Label */}
                  <span className="hidden sm:inline-block absolute left-5 top-1/2 -translate-y-1/2 px-2 py-0.5 rounded text-[10px] font-mono font-bold whitespace-nowrap bg-slate-900/90 text-white border border-slate-700 shadow-md">
                    {node.name.split(' ')[0]}
                  </span>
                </div>
              </div>
            );
          })}

          {/* Quick HUD Banner inside Map */}
          <div className="absolute top-3 left-3 px-3 py-1.5 rounded bg-slate-900/80 backdrop-blur-md border border-slate-700 text-[11px] font-mono text-slate-300">
            <span>VESSEL AIS TRACKING: 71 CONTAINER SHIPS IN TELEMETRY</span>
          </div>
        </div>

        {/* ── Interactive Node Details & Supply Chain Flow Explanation Panel ── */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-5 pt-3">
          {/* Active Node Detail Card */}
          <div className="md:col-span-6 p-5 rounded-lg bg-slate-50 border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200 mb-3">
              <div className="flex items-center gap-2.5">
                <div
                  className="w-8 h-8 rounded-md flex items-center justify-center text-white"
                  style={{ background: getNodeColor(activeNode.status) }}
                >
                  <activeNode.icon className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 leading-tight">
                    {activeNode.name}
                  </h3>
                  <p className="text-xs text-slate-500 font-medium">
                    {activeNode.category} · {activeNode.country}
                  </p>
                </div>
              </div>

              <span
                className="px-2.5 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider text-white"
                style={{ background: getNodeColor(activeNode.status) }}
              >
                {activeNode.status}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-3 mb-4 text-xs">
              <div className="p-2.5 rounded bg-white border border-slate-200">
                <span className="text-[10px] font-semibold text-slate-400 block uppercase">Forecast Delay</span>
                <span className="font-mono font-bold text-slate-900 text-xs mt-0.5 block">{activeNode.delay}</span>
              </div>
              <div className="p-2.5 rounded bg-white border border-slate-200">
                <span className="text-[10px] font-semibold text-slate-400 block uppercase">Active SKUs</span>
                <span className="font-mono font-bold text-slate-900 text-xs mt-0.5 block">{activeNode.skus.toLocaleString()}</span>
              </div>
              <div className="p-2.5 rounded bg-white border border-slate-200">
                <span className="text-[10px] font-semibold text-slate-400 block uppercase">Satellite Ping</span>
                <span className="font-mono font-bold text-emerald-600 text-xs mt-0.5 block">{activeNode.latency}</span>
              </div>
            </div>

            <div className="p-3 rounded bg-white border border-slate-200 text-xs space-y-1.5">
              <div className="flex items-center justify-between text-slate-500 text-[11px]">
                <span className="font-semibold uppercase tracking-wider">Automated Agent Status:</span>
                <span className="font-mono font-medium text-[#8e3a59]">{activeNode.agent}</span>
              </div>
              <p className="text-slate-700 leading-relaxed text-xs">
                {activeNode.action}
              </p>
            </div>
          </div>

          {/* Explanation Guide: How the Digital Twin Uses this Map */}
          <div className="md:col-span-6 p-5 rounded-lg bg-slate-50 border border-slate-200 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 pb-2 border-b border-slate-200 mb-3">
                <Info className="w-4 h-4 text-[#8e3a59]" />
                <h3 className="text-sm font-bold text-slate-900">
                  How the Digital Twin Network Map Works
                </h3>
              </div>

              <div className="space-y-2.5 text-xs text-slate-600 leading-relaxed">
                <div className="flex items-start gap-2">
                  <div className="w-4 h-4 rounded-full bg-slate-200 flex items-center justify-center shrink-0 font-bold text-[10px] text-slate-700 mt-0.5">
                    1
                  </div>
                  <p>
                    <strong className="text-slate-900">Continuous Satellite AIS Ingestion:</strong> Ingests live maritime transponder data for container vessels traversing Suez, Malacca, and Trans-Pacific routes.
                  </p>
                </div>

                <div className="flex items-start gap-2">
                  <div className="w-4 h-4 rounded-full bg-slate-200 flex items-center justify-center shrink-0 font-bold text-[10px] text-slate-700 mt-0.5">
                    2
                  </div>
                  <p>
                    <strong className="text-slate-900">Gradient Boosting Delay Regressor:</strong> Feeds port queuing times and vessel speed variances into the trained ML model to forecast downstream arrival delays ($\Delta L$).
                  </p>
                </div>

                <div className="flex items-start gap-2">
                  <div className="w-4 h-4 rounded-full bg-slate-200 flex items-center justify-center shrink-0 font-bold text-[10px] text-slate-700 mt-0.5">
                    3
                  </div>
                  <p>
                    <strong className="text-slate-900">Autonomous Reroute &amp; Switching Policy:</strong> If a chokepoint exceeds safety buffers, the Buyer Agent autonomously solicits alternate supplier contracts before plant inventory runs dry.
                  </p>
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-200 mt-3 flex items-center justify-between">
              <span className="text-[11px] font-mono text-slate-500">
                TRAINED MODEL ARTIFACT: lead_time_regressor_gb.joblib
              </span>
              <button
                onClick={() => setCurrentPage('simulation')}
                className="text-xs font-semibold text-[#8e3a59] hover:underline flex items-center gap-1"
              >
                Simulate Chokepoint <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* ── Live AI Event Log ── */}
      <div className="p-6 rounded-lg bg-white border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-200">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-[#8e3a59]" />
            <h2 className="text-sm font-bold text-slate-900">
              Live AI Event &amp; Telemetry Log
            </h2>
          </div>
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-100 text-slate-700 border border-slate-200">
            REALTIME LOG
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            {
              tag: 'AUTONOMOUS SOLVER',
              msg: 'Micro-negotiation Round #4 completed with Apex Global. Saved $84,200.',
              sub: 'Unit Price: $148.20 vs $154.00 incumbent',
              time: '10:24 AM',
            },
            {
              tag: 'SUEZ REROUTE ALERT',
              msg: 'Container Vessel MSC Isabella rerouted to Cape of Good Hope corridor.',
              sub: '+6 Days lead time on SKU #MK-902 mitigated by buffer',
              time: '10:18 AM',
            },
            {
              tag: 'TWIN SYNC',
              msg: 'Reconciled Rotterdam Port gateway with Hamburg rail warehouse buffer.',
              sub: 'Inventory delta: 0 variance across 4,120 SKUs',
              time: '10:05 AM',
            },
          ].map((item) => (
            <div
              key={item.tag}
              className="p-4 rounded-md bg-slate-50 border border-slate-200 text-xs space-y-1.5"
            >
              <div className="flex justify-between items-center">
                <span className="font-mono font-bold text-[10px] text-[#8e3a59]">
                  {item.tag}
                </span>
                <span className="font-mono text-[10px] text-slate-400">
                  {item.time}
                </span>
              </div>
              <p className="font-semibold text-slate-900 text-xs leading-snug">
                {item.msg}
              </p>
              <p className="font-mono text-[11px] text-slate-500">
                {item.sub}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
