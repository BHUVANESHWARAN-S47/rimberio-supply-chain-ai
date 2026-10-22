import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { RimberioAPI } from '../services/api';
import { formatINR } from '../utils/currency';
import {
  Brain,
  Shield,
  Bot,
  Truck,
  TrendingDown,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Sparkles,
  ArrowRight,
  MessageSquare,
  Zap,
  Building2,
  Package,
  Layers,
  HelpCircle,
  Paperclip,
  Send,
  Download,
  FileText,
  User,
} from 'lucide-react';

export const CollaborativeAIPage = () => {
  const { user, capabilities, setCurrentPage } = useApp();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [orders, setOrders] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState('Supplier Allocation & Corridor Expedite');
  const [discussing, setDiscussing] = useState(false);
  const [customDiscussion, setCustomDiscussion] = useState(null);
  const [chatInput, setChatInput] = useState('');
  const [chatBusy, setChatBusy] = useState(false);
  const [attachedDocument, setAttachedDocument] = useState(null);
  const [chatMessages, setChatMessages] = useState([
    {
      role: 'assistant',
      agent: 'Admin Orchestrator',
      content: 'I am connected to the Buyer, Risk, Logistics, Decision, and Customer SLA agents. Ask for a decision, upload a contract or invoice, and I will show the evidence chain before recommending an action.',
    },
  ]);
  const [latestDecision, setLatestDecision] = useState(null);
  const [decisionDocument, setDecisionDocument] = useState(null);

  const fetchCollaborativeData = async () => {
    setLoading(true);
    try {
      const [collabRes, poRes] = await Promise.all([
        RimberioAPI.getCollaborativeAI().catch(() => null),
        RimberioAPI.getPurchaseOrders().catch(() => []),
      ]);
      setData(collabRes);
      setOrders(Array.isArray(poRes) ? poRes : []);
    } catch (err) {
      console.warn('Failed to load collaborative AI data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCollaborativeData();
  }, []);

  const handleRunDiscussion = async () => {
    setDiscussing(true);
    try {
      const activeSupplier = orders[0]?.supplier_name || 'Apex Global Logistics';
      const res = await RimberioAPI.runAgentDiscussion({
        topic: selectedTopic,
        supplier_name: activeSupplier,
      });
      setCustomDiscussion(res);
    } catch (err) {
      console.error(err);
    } finally {
      setDiscussing(false);
    }
  };

  const handleDocument = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      setAttachedDocument({
        name: file.name,
        type: file.type || 'application/octet-stream',
        size: file.size,
        content: String(reader.result || '').slice(0, 12000),
      });
    };
    reader.readAsText(file);
  };

  const handleChatSubmit = async (event) => {
    event.preventDefault();
    const message = chatInput.trim();
    if (!message || chatBusy) return;

    setChatMessages((previous) => [...previous, { role: 'user', agent: 'You', content: message }]);
    setChatInput('');
    setChatBusy(true);
    try {
      const response = await RimberioAPI.collaborativeAIChat({
        message,
        target_agent: 'ADMIN_MANAGER_AI',
        history: chatMessages.slice(-8),
        document: attachedDocument,
      });
      setChatMessages((previous) => [
        ...previous,
        { role: 'assistant', agent: 'Admin Orchestrator', content: response.reply },
      ]);
      setLatestDecision(response);
      setAttachedDocument(null);
    } catch (error) {
      setChatMessages((previous) => [
        ...previous,
        { role: 'assistant', agent: 'System', content: `The agent network could not complete this request: ${error.message}` },
      ]);
    } finally {
      setChatBusy(false);
    }
  };

  const handleGenerateDocument = async () => {
    if (!latestDecision) return;
    try {
      const generated = await RimberioAPI.generateDecisionDocument({
        document_id: latestDecision.document_id,
        supplier_name: latestDecision.supplier_name,
        po_number: latestDecision.po_number,
        po_amount: latestDecision.po_amount,
        action: latestDecision.action,
        confidence: latestDecision.confidence,
        topic: latestDecision.topic,
      });
      setDecisionDocument(generated);
      const blob = new Blob([JSON.stringify(generated, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${generated.document_id || 'executive-decision'}.json`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      setChatMessages((previous) => [
        ...previous,
        { role: 'assistant', agent: 'System', content: `Decision document generation failed: ${error.message}` },
      ]);
    }
  };

  const consensus = data?.active_consensus;
  const specialistAgents = data?.specialist_agents_connected || [];

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      {/* ── Header ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-xl bg-white border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider bg-purple-50 text-purple-700 border border-purple-200">
              <Brain className="w-3.5 h-3.5" />
              Executive Multi-Agent Orchestrator
            </span>
            <span className="text-xs text-slate-500">
              {user?.organization?.name || 'Rimberio Global Dynamics'}
            </span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Collaborative AI Decision Hub
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Admin Co-Pilot actively consulting with Buyer, Risk, Logistics, and Decision agents to synthesize executive supply chain policy.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchCollaborativeData}
            disabled={loading}
            className="px-3 py-2 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 transition-colors flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh Agents
          </button>
          <button
            onClick={handleRunDiscussion}
            disabled={discussing}
            className="px-4 py-2 rounded-lg bg-[#8e3a59] hover:bg-[#752d48] text-white text-xs font-semibold shadow-sm transition-all flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            {discussing ? 'Agents Debating...' : 'Run Agent Consultation'}
          </button>
        </div>
      </div>

      {/* ── 5 Specialist Agents Status Cards ── */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Bot className="w-4 h-4 text-[#8e3a59]" />
            Connected Specialist Role Agents ({specialistAgents.length || 5})
          </h2>
          <span className="text-xs text-emerald-600 font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
            All Specialized Agents Online
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
          {specialistAgents.map((ag) => (
            <div
              key={ag.code}
              className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm hover:border-[#8e3a59]/40 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono font-bold uppercase px-1.5 py-0.5 rounded bg-slate-100 text-slate-700">
                    {ag.domain}
                  </span>
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                </div>
                <h3 className="font-bold text-slate-900 text-xs line-clamp-1">{ag.name}</h3>
                <p className="text-[11px] text-slate-500 mt-1 line-clamp-2 leading-relaxed">
                  {ag.specialty}
                </p>
              </div>
              <div className="mt-3 pt-2.5 border-t border-slate-100 text-[10px] text-slate-500">
                Partner: <strong className="text-slate-800">{ag.lead_user}</strong>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── ChatGPT-style multi-agent console ── */}
      <section className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        <div className="xl:col-span-8 rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div>
              <h2 className="font-bold text-slate-900 flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-[#8e3a59]" />
                Multi-Agent Chat Console
              </h2>
              <p className="text-xs text-slate-500 mt-1">One conversation, five specialist models, one auditable decision trace.</p>
            </div>
            <span className="rounded-md border border-slate-200 bg-slate-50 px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-600">
              Admin Manager AI routes all specialist work
            </span>
          </div>

          <div className="h-[390px] overflow-y-auto p-5 space-y-4 bg-slate-50/60">
            {chatMessages.map((message, index) => (
              <div key={`${message.agent}-${index}`} className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : ''}`}>
                {message.role !== 'user' && <div className="w-7 h-7 shrink-0 rounded-full bg-[#8e3a59] text-white flex items-center justify-center"><Bot className="w-4 h-4" /></div>}
                <div className={`max-w-[86%] rounded-xl px-4 py-3 text-sm whitespace-pre-wrap leading-relaxed ${message.role === 'user' ? 'bg-slate-900 text-white' : 'bg-white border border-slate-200 text-slate-700'}`}>
                  <div className="text-[10px] font-bold uppercase tracking-wider mb-1 opacity-60">{message.agent}</div>
                  {message.content}
                </div>
                {message.role === 'user' && <div className="w-7 h-7 shrink-0 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center"><User className="w-4 h-4" /></div>}
              </div>
            ))}
            {chatBusy && <div className="text-xs text-slate-500 flex items-center gap-2"><RefreshCw className="w-3.5 h-3.5 animate-spin" /> Agents are comparing evidence...</div>}
          </div>

          <form onSubmit={handleChatSubmit} className="p-4 border-t border-slate-200">
            {attachedDocument && (
              <div className="mb-2 flex items-center justify-between rounded-md bg-emerald-50 border border-emerald-200 px-3 py-2 text-xs text-emerald-800">
                <span className="flex items-center gap-2"><FileText className="w-3.5 h-3.5" /> {attachedDocument.name} ready for agent review</span>
                <button type="button" onClick={() => setAttachedDocument(null)} className="font-bold">Remove</button>
              </div>
            )}
            <div className="flex items-end gap-2 rounded-xl border border-slate-300 bg-white p-2 focus-within:border-[#8e3a59]">
              <label title="Attach a contract, invoice, CSV, TXT, or JSON document" className="p-2 cursor-pointer text-slate-500 hover:text-[#8e3a59]">
                <Paperclip className="w-4 h-4" />
                <input type="file" accept=".pdf,.csv,.txt,.json,.md" onChange={handleDocument} className="hidden" />
              </label>
              <textarea
                value={chatInput}
                onChange={(event) => setChatInput(event.target.value)}
                onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); handleChatSubmit(event); } }}
                placeholder="Ask the agent network for a sourcing or logistics decision..."
                rows={2}
                className="flex-1 resize-none border-0 text-sm text-slate-800 outline-none placeholder:text-slate-400"
              />
              <button type="submit" disabled={chatBusy || !chatInput.trim()} title="Send to agent network" className="rounded-lg bg-[#8e3a59] p-2.5 text-white disabled:opacity-40">
                <Send className="w-4 h-4" />
              </button>
            </div>
          </form>
        </div>

        <div className="xl:col-span-4 space-y-4">
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-sm text-slate-900">Decision Trace</h3>
              <span className="text-[10px] font-bold uppercase text-emerald-700">{capabilities?.length || specialistAgents.length} capabilities</span>
            </div>
            {latestDecision ? (
              <div className="space-y-3 text-xs">
                <div className="rounded-lg bg-emerald-50 border border-emerald-200 p-3">
                  <p className="font-bold text-emerald-900">{latestDecision.action}</p>
                  <p className="text-emerald-800 mt-1">Confidence: {(latestDecision.confidence * 100).toFixed(0)}%</p>
                </div>
                <p className="text-slate-600">{latestDecision.topic}</p>
                <div className="space-y-2">
                  {(latestDecision.agent_debates || []).map((debate) => (
                    <div key={debate.agent} className="border-l-2 border-[#8e3a59] pl-3">
                      <p className="font-bold text-slate-800">{debate.agent}</p>
                      <p className="text-slate-500 mt-0.5">{debate.status}</p>
                    </div>
                  ))}
                </div>
                <button onClick={handleGenerateDocument} className="w-full rounded-lg bg-slate-900 px-3 py-2 text-xs font-bold text-white flex items-center justify-center gap-2">
                  <Download className="w-3.5 h-3.5" /> Generate Decision Document
                </button>
                {decisionDocument && <p className="text-[10px] text-emerald-700">Document {decisionDocument.document_id} generated and downloaded.</p>}
              </div>
            ) : (
              <div className="text-xs text-slate-500 space-y-3">
                <p>Send a question to create a trace showing how each specialist agent contributes to the final recommendation.</p>
                <button onClick={() => setCurrentPage('decision_center')} className="text-[#8e3a59] font-bold">Open Adaptive Decision Center</button>
              </div>
            )}
          </div>
          {attachedDocument && <div className="rounded-xl border border-blue-200 bg-blue-50 p-4 text-xs text-blue-900"><strong>Document context active.</strong><p className="mt-1">The uploaded content will be passed to the orchestrator with the next message for contract, invoice, or shipment evidence review.</p></div>}
        </div>
      </section>

      {/* ── Active Consensus Banner ── */}
      {consensus && (
        <div className="p-6 rounded-xl bg-gradient-to-r from-purple-900 via-indigo-900 to-slate-900 text-white shadow-lg relative overflow-hidden">
          <div className="relative z-10">
            <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
              <span className="px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-xs font-semibold uppercase tracking-wider text-purple-200 border border-white/10 flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                Multi-Agent Synthesis Agreement
              </span>
              <span className="text-xs font-mono text-purple-200">
                Confidence Score: <strong className="text-white text-sm">{(consensus.confidence_score * 100).toFixed(0)}%</strong>
              </span>
            </div>

            <h2 className="text-xl font-bold tracking-tight mb-2">
              {consensus.title}
            </h2>
            <div className="inline-block px-3 py-1.5 rounded-lg bg-emerald-500/20 border border-emerald-400/30 text-emerald-300 font-bold text-sm tracking-wide mb-4">
              RECOMMENDED ACTION: {consensus.executive_decision}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-3 border-t border-white/10 text-xs">
              <div>
                <span className="text-purple-300 block text-[11px]">Cost Savings Variance</span>
                <strong className="text-white text-sm">{consensus.cost_variance}</strong>
              </div>
              <div>
                <span className="text-purple-300 block text-[11px]">SLA Target Adherence</span>
                <strong className="text-white text-sm">{consensus.sla_protection}</strong>
              </div>
              <div>
                <span className="text-purple-300 block text-[11px]">Active Action Item</span>
                <strong className="text-white text-sm">{consensus.action_items?.[0] || 'PO Issuance with negotiated discount'}</strong>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Two Columns: Dialogue Arena & Orders Chosen Suppliers ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (7 Cols): Multi-Agent Dialogue Transcript */}
        <div className="lg:col-span-7 bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200">
            <div>
              <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-[#8e3a59]" />
                Live Agent Discussion & Debate Arena
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Admin Collaborative Orchestrator querying specialist role agents
              </p>
            </div>
            <span className="text-xs text-slate-400 font-mono">Real-time Stream</span>
          </div>

          {/* Transcript Feed */}
          <div className="space-y-3.5 max-h-[500px] overflow-y-auto pr-1">
            {consensus?.discussion_log?.map((msg, idx) => {
              const isAdmin = msg.role.includes('Orchestrator') || msg.role.includes('Final');
              const isBuyer = msg.role.includes('Pricing');
              const isRisk = msg.role.includes('Risk');
              const isLogistics = msg.role.includes('Corridor');
              const isDecision = msg.role.includes('Policy');

              return (
                <div
                  key={idx}
                  className={`p-3.5 rounded-xl border text-xs leading-relaxed transition-all ${
                    isAdmin
                      ? 'bg-purple-50/70 border-purple-200 text-purple-950 font-medium'
                      : isBuyer
                      ? 'bg-rose-50/50 border-rose-200 text-slate-800'
                      : isRisk
                      ? 'bg-blue-50/50 border-blue-200 text-slate-800'
                      : isLogistics
                      ? 'bg-amber-50/50 border-amber-200 text-slate-800'
                      : 'bg-emerald-50/50 border-emerald-200 text-slate-800'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-bold text-slate-900 flex items-center gap-1.5">
                      <Bot className="w-3.5 h-3.5 text-[#8e3a59]" />
                      {msg.speaker}
                    </span>
                    <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-white/80 border border-slate-200 text-slate-600">
                      {msg.role}
                    </span>
                  </div>
                  <p className="text-slate-700">{msg.message}</p>
                </div>
              );
            })}

            {/* Custom Consultation Result if run */}
            {customDiscussion && (
              <div className="p-4 rounded-xl bg-slate-900 text-white space-y-3 mt-4 border border-slate-800">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-amber-400 uppercase tracking-wider">
                    On-Demand Agent Consultation Output
                  </span>
                  <span className="text-[11px] font-mono text-slate-400">
                    Confidence: {(customDiscussion.consensus_confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="text-sm font-semibold text-emerald-300">
                  {customDiscussion.synthesized_suggestion}
                </p>
                <div className="space-y-1.5 pt-2 border-t border-slate-800">
                  {customDiscussion.transcripts.map((t, i) => (
                    <div key={i} className="text-xs text-slate-300">
                      <strong className="text-white">{t.agent}:</strong> {t.text}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Column (5 Cols): Orders & Chosen Suppliers Overview */}
        <div className="lg:col-span-5 bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200">
            <div>
              <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                <Building2 className="w-4 h-4 text-[#8e3a59]" />
                Recent Orders & Awarded Suppliers
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Real purchase order allocations chosen across departments
              </p>
            </div>
            <span className="text-xs font-mono text-slate-500">
              {orders.length} Orders Placed
            </span>
          </div>

          <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
            {orders.slice(0, 7).map((po) => (
              <div
                key={po.id}
                className="p-3 rounded-lg border border-slate-200 hover:border-slate-300 bg-slate-50/40 transition-colors text-xs"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-mono font-bold text-slate-900">{po.po_number}</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                      po.status === 'DELIVERED'
                        ? 'bg-emerald-100 text-emerald-800'
                        : po.status === 'SHIPPED'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-amber-100 text-amber-800'
                    }`}
                  >
                    {po.status}
                  </span>
                </div>

                <div className="flex items-center justify-between text-slate-800 font-semibold mb-1">
                  <span className="truncate pr-2">{po.supplier_name || 'Strategic Supplier'}</span>
                  <span className="font-mono font-bold text-slate-900 shrink-0">
                    {formatINR(po.total_amount)}
                  </span>
                </div>

                <div className="text-[11px] text-slate-500 flex items-center justify-between pt-1 border-t border-slate-200/60">
                  <span>Product: {po.product_name || 'Industrial Batch'}</span>
                  <span className="text-[#8e3a59] font-medium">{po.decision_label || 'Awarded via AI'}</span>
                </div>
              </div>
            ))}

            {orders.length === 0 && (
              <div className="p-8 text-center text-slate-400 text-xs">
                No active purchase orders recorded yet.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
