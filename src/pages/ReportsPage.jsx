import React from 'react';
import { FileText, Download, ExternalLink } from 'lucide-react';

export const ReportsPage = () => {
  const reports = [
    {
      id: 'RPT-2026-Q4-001',
      title: 'Q4 2026 Supply Chain Performance Analysis',
      date: 'Oct 05, 2026',
      status: 'PUBLISHED',
      pages: 42,
      category: 'QUARTERLY',
      size: '3.2 MB',
    },
    {
      id: 'RPT-2026-SUP-011',
      title: 'Suez Canal Disruption Post-Mortem Report',
      date: 'Oct 04, 2026',
      status: 'PUBLISHED',
      pages: 18,
      category: 'DISRUPTION',
      size: '1.1 MB',
    },
    {
      id: 'RPT-2026-NEG-042',
      title: 'Micro-Negotiation ROI Summary — Oct 2026',
      date: 'Oct 03, 2026',
      status: 'PUBLISHED',
      pages: 12,
      category: 'FINANCIAL',
      size: '0.8 MB',
    },
    {
      id: 'RPT-2026-ESG-007',
      title: 'Vendor ESG Compliance & Sustainability Audit',
      date: 'Sep 30, 2026',
      status: 'DRAFT',
      pages: 28,
      category: 'ESG',
      size: '2.4 MB',
    },
    {
      id: 'RPT-2026-ARC-001',
      title: 'RIMBERIO Platform Architecture Overview (v4.2)',
      date: 'Sep 28, 2026',
      status: 'PUBLISHED',
      pages: 64,
      category: 'TECHNICAL',
      size: '5.0 MB',
    },
  ];

  const catColors = {
    QUARTERLY: { badge: 'badge-healthy' },
    DISRUPTION: { badge: 'badge-teal' },
    FINANCIAL: { badge: 'badge-bone' },
    ESG: { badge: 'badge-healthy' },
    TECHNICAL: { badge: 'badge-bone' },
  };

  return (
    <div className="space-y-5 pb-12">
      <div
        className="p-5 rounded-[6px] bg-white border border-[#d9dad3]"
      >
        <div className="flex items-center gap-2 mb-1">
          <span className="badge badge-healthy">5 REPORTS AVAILABLE</span>
        </div>
        <h1 className="text-xl md:text-2xl font-bold text-black" style={{ letterSpacing: '-0.02em', color: '#000000' }}>
          REPORTS & PLATFORM ARCHITECTURE
        </h1>
        <p className="text-xs text-[#5c5c5c] mt-0.5">
          Downloadable audit reports, disruption post-mortems, ESG scorecards, and the full RIMBERIO technical specification.
        </p>
      </div>

      <div className="rounded-[6px] overflow-hidden bg-white border border-[#d9dad3]">
        <div className="px-5 py-2.5 flex items-center gap-2 border-b border-[#d9dad3] bg-[#edede8]">
          <FileText className="w-4 h-4 text-black" />
          <span className="rim-section-title text-[10px] text-black font-bold">
            Document Library
          </span>
        </div>

        <table className="w-full">
          <thead>
            <tr>
              {['Document', 'Category', 'Date', 'Status', 'Pages', 'Actions'].map((col) => (
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
            {reports.map((r) => {
              const cc = catColors[r.category] || { badge: 'badge-bone' };
              return (
                <tr key={r.id} className="rim-tr">
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-2.5">
                      <div className="w-7 h-7 rounded-[4px] flex items-center justify-center shrink-0 bg-[#edede8] border border-[#d9dad3]">
                        <FileText className="w-3.5 h-3.5 text-black" />
                      </div>
                      <div>
                        <p className="text-xs font-bold text-black" style={{ color: '#000000' }}>
                          {r.title}
                        </p>
                        <p className="rim-mono text-[10px] text-[#5c5c5c]">
                          {r.id} · {r.size}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-3.5">
                    <span className={`badge ${cc.badge}`}>{r.category}</span>
                  </td>
                  <td className="px-5 py-3.5 text-xs text-[#5c5c5c]">{r.date}</td>
                  <td className="px-5 py-3.5">
                    <span
                      className={`badge ${r.status === 'PUBLISHED' ? 'badge-healthy' : 'badge-bone'}`}
                    >
                      {r.status}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-xs text-[#5c5c5c]">{r.pages} pgs</td>
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => alert(`Downloading ${r.title}...`)}
                        className="p-1.5 rounded-[4px] border border-[#d9dad3] hover:border-black transition-colors"
                        title="Download PDF"
                      >
                        <Download className="w-3.5 h-3.5 text-black" />
                      </button>
                      <button
                        onClick={() => alert(`Opening preview of ${r.title}...`)}
                        className="p-1.5 rounded-[4px] border border-[#d9dad3] hover:border-black transition-colors"
                        title="Open Preview"
                      >
                        <ExternalLink className="w-3.5 h-3.5 text-black" />
                      </button>
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
