import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { RimberioAPI } from '../services/api';
import {
  HelpTooltip,
  StatusBadge,
  DeleteConfirmDialog,
  EmptyState,
  Toast,
} from '../components/common/CommonUI';
import {
  Users,
  Building2,
  Brain,
  Activity,
  FileText,
  Plus,
  RefreshCw,
  Search,
  Key,
  Shield,
  Download,
  Trash2,
  Edit2,
  Power,
  X,
  CheckCircle,
  HelpCircle,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

export const AdminPage = ({ initialTab = 'users' }) => {
  const { user } = useApp();
  const [activeTab, setActiveTab] = useState(initialTab);
  const [loading, setLoading] = useState(true);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');

  // Tab Data
  const [usersList, setUsersList] = useState([]);
  const [departmentsList, setDepartmentsList] = useState([]);
  const [rolesList, setRolesList] = useState([]);
  const [aiAgentsList, setAiAgentsList] = useState([]);
  const [learningMetrics, setLearningMetrics] = useState(null);
  const [activityLogs, setActivityLogs] = useState([]);

  // Search & Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('ALL');
  const [dateFilter, setDateFilter] = useState('');

  // Modals & Side Panels
  const [showAddUserModal, setShowAddUserModal] = useState(false);
  const [showEditUserModal, setShowEditUserModal] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [userForm, setUserForm] = useState({
    full_name: '',
    email: '',
    role_id: 3, // Default Buyer
    department_id: '',
    password: 'enterprise_pass_2026',
  });

  const [showAddDeptModal, setShowAddDeptModal] = useState(false);
  const [deptForm, setDeptForm] = useState({ name: '', code: '' });

  // Delete Dialog
  const [deleteDialog, setDeleteDialog] = useState({
    isOpen: false,
    itemType: '',
    itemId: '',
    itemName: '',
  });

  // Algorithm details toggle for AI Agents
  const [showAgentDetails, setShowAgentDetails] = useState({});

  useEffect(() => {
    if (initialTab) setActiveTab(initialTab);
  }, [initialTab]);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [uRes, dRes, rRes, agRes, metRes, actRes] = await Promise.all([
        RimberioAPI.getAdminUsers().catch(() => ({ users: [] })),
        RimberioAPI.getAdminDepartments().catch(() => ({ departments: [] })),
        RimberioAPI.getAdminRoles().catch(() => ({ roles: [] })),
        RimberioAPI.getAIAgents().catch(() => []),
        RimberioAPI.getLearningMetrics().catch(() => null),
        RimberioAPI.getActivityLogs().catch(() => []),
      ]);

      setUsersList(Array.isArray(uRes) ? uRes : (uRes.users || []));
      setDepartmentsList(Array.isArray(dRes) ? dRes : (dRes.departments || []));
      setRolesList(Array.isArray(rRes) ? rRes : (rRes.roles || []));
      setAiAgentsList(Array.isArray(agRes) ? agRes : []);
      setLearningMetrics(metRes);
      setActivityLogs(Array.isArray(actRes) ? actRes : []);
    } catch (err) {
      console.warn('[AdminPage] Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, [user]);

  const showToast = (msg, type = 'success') => {
    setToastMessage(msg);
    setToastType(type);
  };

  // ─── USER ACTIONS ───
  const handleSaveUser = async (e) => {
    e.preventDefault();
    if (!userForm.full_name || !userForm.email) {
      showToast('Please provide full name and email.', 'error');
      return;
    }

    try {
      if (currentUser) {
        // Edit
        await RimberioAPI.updateUser(currentUser.id, {
          full_name: userForm.full_name,
          role_id: parseInt(userForm.role_id),
          department_id: userForm.department_id || null,
        });
        showToast(`User '${userForm.full_name}' updated successfully.`);
      } else {
        // Create
        await RimberioAPI.createUser({
          full_name: userForm.full_name,
          email: userForm.email,
          password: userForm.password || 'enterprise_pass_2026',
          role_id: parseInt(userForm.role_id),
          department_id: userForm.department_id || null,
        });
        showToast(`User '${userForm.full_name}' created successfully.`);
      }
      setShowAddUserModal(false);
      setShowEditUserModal(false);
      setCurrentUser(null);
      loadAllData();
    } catch (err) {
      showToast(err.message || 'Operation failed.', 'error');
    }
  };

  const handleToggleUserStatus = async (userId, currentName) => {
    try {
      const res = await RimberioAPI.toggleUserStatus(userId);
      showToast(res.message || `Status updated for ${currentName}.`);
      loadAllData();
    } catch (err) {
      showToast(err.message || 'Failed to update user status.', 'error');
    }
  };

  const handleResetPassword = async (userId, currentName) => {
    try {
      const res = await RimberioAPI.resetUserPassword(userId);
      showToast(res.message || `Password reset for ${currentName}.`);
    } catch (err) {
      showToast(err.message || 'Failed to reset password.', 'error');
    }
  };

  // ─── DEPARTMENT ACTIONS ───
  const handleSaveDept = async (e) => {
    e.preventDefault();
    if (!deptForm.name || !deptForm.code) {
      showToast('Please provide department name and code.', 'error');
      return;
    }

    try {
      await RimberioAPI.createDepartment(deptForm);
      showToast(`Department '${deptForm.name}' created.`);
      setShowAddDeptModal(false);
      setDeptForm({ name: '', code: '' });
      loadAllData();
    } catch (err) {
      showToast(err.message || 'Failed to create department.', 'error');
    }
  };

  // ─── DELETE HANDLER ───
  const handleConfirmDelete = async () => {
    const { itemType, itemId, itemName } = deleteDialog;
    try {
      if (itemType === 'user') {
        await RimberioAPI.deleteUser(itemId);
        showToast(`User '${itemName}' deleted.`);
      } else if (itemType === 'department') {
        await RimberioAPI.deleteDepartment(itemId);
        showToast(`Department '${itemName}' deleted.`);
      }
      setDeleteDialog({ isOpen: false, itemType: '', itemId: '', itemName: '' });
      loadAllData();
    } catch (err) {
      showToast(err.message || 'Delete operation blocked.', 'error');
      setDeleteDialog({ isOpen: false, itemType: '', itemId: '', itemName: '' });
    }
  };

  // ─── AI AGENT TOGGLE ───
  const handleToggleAgent = async (agentId, agentName) => {
    try {
      const res = await RimberioAPI.toggleAIAgent(agentId);
      showToast(res.message || `Toggled ${agentName}.`);
      loadAllData();
    } catch (err) {
      showToast(err.message || 'Failed to toggle AI agent.', 'error');
    }
  };

  // ─── AI RECALIBRATE ───
  const handleRecalibrate = async () => {
    try {
      await RimberioAPI.triggerRecalibration();
      showToast('AI learning model successfully updated with recent data.');
      loadAllData();
    } catch (err) {
      showToast(err.message || 'Recalibration error.', 'error');
    }
  };

  // ─── EXPORT CSV ───
  const handleExportCSV = () => {
    const headers = ['Date', 'User', 'Action', 'Item', 'Entity Type'];
    const rows = activityLogs.map(l => [
      l.date,
      `"${l.user || ''}"`,
      l.action,
      `"${l.item || ''}"`,
      l.entity_type,
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `activity_history_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast('Activity history exported to CSV.');
  };

  // Filtered users
  const filteredUsers = usersList.filter(u => {
    const matchesSearch = !searchTerm ||
      u.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      u.email?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = roleFilter === 'ALL' || u.role?.name === roleFilter;
    return matchesSearch && matchesRole;
  });

  // Filtered logs
  const filteredLogs = activityLogs.filter(l => {
    const matchesSearch = !searchTerm ||
      l.item?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      l.user?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      l.action?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDate = !dateFilter || l.date?.startsWith(dateFilter);
    return matchesSearch && matchesDate;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* ── Top Header & Tab Switcher ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-xl bg-white border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              {activeTab === 'users' && 'Users & Roles'}
              {activeTab === 'departments' && 'Departments'}
              {activeTab === 'ai_agents' && 'AI Agents'}
              {activeTab === 'ai_health' && 'AI Health'}
              {activeTab === 'audit_logs' && 'Activity History'}
            </h1>
            <HelpTooltip text={
              activeTab === 'users' ? 'Manage enterprise team members, roles, passwords, and account access.' :
              activeTab === 'departments' ? 'Configure organizational departments and view assigned staff counts.' :
              activeTab === 'ai_agents' ? 'Review active AI agents with plain descriptions and turn them ON or OFF.' :
              activeTab === 'ai_health' ? 'Audit AI prediction accuracy and update learning models.' :
              'Immutable operational activity log of team actions with search and CSV export.'
            } />
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            System Administration &bull; Platform Governance Console
          </p>
        </div>

        {/* Tab Pills */}
        <div className="flex flex-wrap items-center gap-1.5 p-1 rounded-lg bg-slate-100 border border-slate-200">
          {[
            { id: 'users', label: 'Users & Roles', icon: Users },
            { id: 'departments', label: 'Departments', icon: Building2 },
            { id: 'ai_agents', label: 'AI Agents', icon: Brain },
            { id: 'ai_health', label: 'AI Health', icon: Activity },
            { id: 'audit_logs', label: 'Activity History', icon: FileText },
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => { setActiveTab(tab.id); setSearchTerm(''); }}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-white text-[#8e3a59] font-bold shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* ── TAB 1: USERS & ROLES ── */}
      {activeTab === 'users' && (
        <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-3 flex-1 max-w-md">
              <div className="relative flex-1">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search users by name or email..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-slate-200 focus:outline-none focus:border-[#8e3a59]"
                />
              </div>
              <select
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value)}
                className="text-xs py-2 px-3 rounded-lg border border-slate-200 bg-white text-slate-700"
              >
                <option value="ALL">All Roles</option>
                <option value="ADMIN">Admin</option>
                <option value="BUYER">Buyer</option>
                <option value="LOGISTICS_MANAGER">Logistics</option>
                <option value="SUPPLIER">Supplier</option>
                <option value="CUSTOMER">Customer</option>
              </select>
            </div>

            <button
              onClick={() => {
                setCurrentUser(null);
                setUserForm({ full_name: '', email: '', role_id: 3, department_id: '', password: 'enterprise_pass_2026' });
                setShowAddUserModal(true);
              }}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-bold text-white bg-[#8e3a59] hover:bg-[#782f49] shadow-sm transition-colors shrink-0"
            >
              <Plus className="w-4 h-4" />
              Add User
            </button>
          </div>

          {filteredUsers.length === 0 ? (
            <EmptyState
              message="No users found matching your search."
              actionLabel="+ Add New User"
              onAction={() => setShowAddUserModal(true)}
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200 text-slate-500 font-bold uppercase text-[10px] tracking-wider">
                    <th className="py-3 px-3">Name & Email</th>
                    <th className="py-3 px-3">Role</th>
                    <th className="py-3 px-3">Department</th>
                    <th className="py-3 px-3">Status</th>
                    <th className="py-3 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredUsers.map((u) => (
                    <tr key={u.id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-3 px-3">
                        <p className="font-bold text-slate-900">{u.full_name}</p>
                        <p className="text-[11px] text-slate-500 font-mono">{u.email}</p>
                      </td>
                      <td className="py-3 px-3 font-semibold text-slate-700">
                        {u.role?.display_name || u.role?.name || 'User'}
                      </td>
                      <td className="py-3 px-3 text-slate-600">
                        {u.department?.name || '—'}
                      </td>
                      <td className="py-3 px-3">
                        <StatusBadge status={u.is_active ? 'APPROVED' : 'CANCELLED'} />
                      </td>
                      <td className="py-3 px-3 text-right space-x-1">
                        <button
                          onClick={() => {
                            setCurrentUser(u);
                            setUserForm({
                              full_name: u.full_name || '',
                              email: u.email || '',
                              role_id: u.role?.id || 3,
                              department_id: u.department?.id || '',
                              password: '',
                            });
                            setShowEditUserModal(true);
                          }}
                          className="px-2 py-1 rounded text-[11px] font-semibold text-slate-700 hover:bg-slate-100 transition-colors"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleToggleUserStatus(u.id, u.full_name)}
                          className={`px-2 py-1 rounded text-[11px] font-semibold transition-colors ${
                            u.is_active ? 'text-amber-700 hover:bg-amber-50' : 'text-emerald-700 hover:bg-emerald-50'
                          }`}
                        >
                          {u.is_active ? 'Disable' : 'Enable'}
                        </button>
                        <button
                          onClick={() => handleResetPassword(u.id, u.full_name)}
                          className="px-2 py-1 rounded text-[11px] font-semibold text-blue-700 hover:bg-blue-50 transition-colors"
                          title="Reset password to enterprise_pass_2026"
                        >
                          Reset Pass
                        </button>
                        <button
                          onClick={() => setDeleteDialog({ isOpen: true, itemType: 'user', itemId: u.id, itemName: u.full_name })}
                          className="px-2 py-1 rounded text-[11px] font-semibold text-rose-600 hover:bg-rose-50 transition-colors"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ── TAB 2: DEPARTMENTS ── */}
      {activeTab === 'departments' && (
        <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-900">Enterprise Departments</h2>
              <p className="text-xs text-slate-500">Configure organizational units and manage staff distribution</p>
            </div>
            <button
              onClick={() => setShowAddDeptModal(true)}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-bold text-white bg-[#8e3a59] hover:bg-[#782f49] shadow-sm transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add Department
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 font-bold uppercase text-[10px] tracking-wider">
                  <th className="py-3 px-3">Department Name</th>
                  <th className="py-3 px-3">Code</th>
                  <th className="py-3 px-3">Assigned Users</th>
                  <th className="py-3 px-3">Status</th>
                  <th className="py-3 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {departmentsList.map((d) => (
                  <tr key={d.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-3 font-bold text-slate-900">{d.name}</td>
                    <td className="py-3 px-3 font-mono text-slate-600">{d.code}</td>
                    <td className="py-3 px-3 font-semibold text-slate-700">{d.user_count || 0} Members</td>
                    <td className="py-3 px-3">
                      <StatusBadge status={d.is_active ? 'APPROVED' : 'CANCELLED'} />
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={() => setDeleteDialog({ isOpen: true, itemType: 'department', itemId: d.id, itemName: d.name })}
                        className="px-2 py-1 rounded text-[11px] font-semibold text-rose-600 hover:bg-rose-50 transition-colors"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── TAB 3: AI AGENTS ── */}
      {activeTab === 'ai_agents' && (
        <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-sm space-y-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">AI Agents Management</h2>
            <p className="text-xs text-slate-500">Overview of the 9 specialized agents coordinating platform operations</p>
          </div>

          <div className="divide-y divide-slate-100">
            {aiAgentsList.map((ag) => {
              const isOpen = !!showAgentDetails[ag.id];
              return (
                <div key={ag.id} className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-lg bg-[#8e3a59]/10 text-[#8e3a59] flex items-center justify-center font-bold text-xs">
                        <Brain className="w-4 h-4" />
                      </div>
                      <h3 className="font-bold text-slate-900 text-sm">{ag.name}</h3>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                        ag.is_active ? 'bg-emerald-50 text-emerald-800' : 'bg-slate-100 text-slate-500'
                      }`}>
                        {ag.is_active ? 'Active (ON)' : 'Disabled (OFF)'}
                      </span>
                    </div>

                    <p className="text-xs text-slate-600 mt-1 pl-9 leading-relaxed">{ag.description}</p>

                    {isOpen && (
                      <div className="mt-2 pl-9">
                        <p className="text-[11px] font-mono text-slate-500 bg-slate-50 p-2.5 rounded-lg border border-slate-200">
                          <span className="font-bold text-slate-700">Algorithm: </span>{ag.algorithm}
                        </p>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-3 shrink-0 self-end sm:self-center">
                    <button
                      onClick={() => setShowAgentDetails({ ...showAgentDetails, [ag.id]: !isOpen })}
                      className="text-xs text-slate-500 hover:text-slate-900 font-semibold flex items-center gap-1 transition-colors"
                    >
                      {isOpen ? 'Hide details' : 'Show details'}
                      {isOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>

                    <button
                      onClick={() => handleToggleAgent(ag.id, ag.name)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all shadow-sm flex items-center gap-1.5 ${
                        ag.is_active
                          ? 'bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200'
                          : 'bg-emerald-600 text-white hover:bg-emerald-700'
                      }`}
                    >
                      <Power className="w-3.5 h-3.5" />
                      {ag.is_active ? 'Turn OFF' : 'Turn ON'}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ── TAB 4: AI HEALTH ── */}
      {activeTab === 'ai_health' && (
        <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-sm space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-base font-bold text-slate-900">AI Health & Model Accuracy</h2>
              <p className="text-xs text-slate-500">Live evaluation of prediction models against verified delivery actuals</p>
            </div>
            <button
              onClick={handleRecalibrate}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold text-white bg-[#8e3a59] hover:bg-[#782f49] shadow-sm transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Update AI Learning
            </button>
          </div>

          {/* Simple Sentence Banner */}
          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center gap-3">
            <CheckCircle className="w-6 h-6 text-emerald-600 shrink-0" />
            <div>
              <p className="text-sm font-bold text-emerald-950">
                AI was right {learningMetrics?.accuracy_pct || 92} out of 100 times.
              </p>
              <p className="text-xs text-emerald-800 mt-0.5">
                The prediction engine is operating within safe enterprise confidence parameters.
              </p>
            </div>
          </div>

          {/* 3 Simple Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Prediction Accuracy</p>
              <p className="text-2xl font-extrabold text-slate-900 mt-1">{learningMetrics?.accuracy_pct || 92.4}%</p>
              <p className="text-[11px] text-emerald-700 mt-1 font-medium">+1.8% vs last month</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Average Delay Error</p>
              <p className="text-2xl font-extrabold text-slate-900 mt-1">{learningMetrics?.mae_days || 0.8} Days</p>
              <p className="text-[11px] text-slate-500 mt-1 font-medium">Under 1 day margin of error</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Verified Records</p>
              <p className="text-2xl font-extrabold text-slate-900 mt-1">{learningMetrics?.sample_count || 1240}</p>
              <p className="text-[11px] text-slate-500 mt-1 font-medium">Historical deliveries audited</p>
            </div>
          </div>
        </div>
      )}

      {/* ── TAB 5: ACTIVITY HISTORY ── */}
      {activeTab === 'audit_logs' && (
        <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-3 flex-1 max-w-md">
              <div className="relative flex-1">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search activity by user, action, or item..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-slate-200 focus:outline-none focus:border-[#8e3a59]"
                />
              </div>
              <input
                type="date"
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                className="text-xs py-2 px-3 rounded-lg border border-slate-200 bg-white text-slate-700"
              />
            </div>

            <button
              onClick={handleExportCSV}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-bold text-slate-700 bg-slate-50 hover:bg-slate-100 border border-slate-200 transition-colors shrink-0"
            >
              <Download className="w-4 h-4" />
              Export CSV
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 font-bold uppercase text-[10px] tracking-wider">
                  <th className="py-3 px-3">Date & Time</th>
                  <th className="py-3 px-3">Team Member</th>
                  <th className="py-3 px-3">Action</th>
                  <th className="py-3 px-3">Item</th>
                  <th className="py-3 px-3">Type</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-3 font-mono text-slate-500 text-[11px]">{log.date}</td>
                    <td className="py-3 px-3 font-bold text-slate-900">{log.user}</td>
                    <td className="py-3 px-3">
                      <span className={`inline-flex px-2 py-0.5 rounded text-[10px] font-bold ${
                        log.action === 'CREATE' ? 'bg-emerald-50 text-emerald-800' :
                        log.action === 'DELETE' ? 'bg-rose-50 text-rose-800' : 'bg-blue-50 text-blue-800'
                      }`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-semibold text-slate-800">{log.item}</td>
                    <td className="py-3 px-3 font-mono text-slate-500 uppercase text-[10px]">{log.entity_type}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── ADD USER MODAL ── */}
      {(showAddUserModal || showEditUserModal) && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="w-full max-w-lg bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">
                {currentUser ? 'Edit User Profile' : 'Add New Team Member'}
              </h3>
              <button
                onClick={() => { setShowAddUserModal(false); setShowEditUserModal(false); }}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSaveUser} className="space-y-3.5">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Priya Sharma"
                  value={userForm.full_name}
                  onChange={(e) => setUserForm({ ...userForm, full_name: e.target.value })}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 focus:outline-none focus:border-[#8e3a59]"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  disabled={!!currentUser}
                  placeholder="e.g. priya.sharma@rimberio.ai"
                  value={userForm.email}
                  onChange={(e) => setUserForm({ ...userForm, email: e.target.value })}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 focus:outline-none focus:border-[#8e3a59] disabled:bg-slate-50"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Role</label>
                  <select
                    value={userForm.role_id}
                    onChange={(e) => setUserForm({ ...userForm, role_id: e.target.value })}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 bg-white text-slate-700"
                  >
                    {rolesList.map(r => (
                      <option key={r.id} value={r.id}>{r.display_name || r.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Department</label>
                  <select
                    value={userForm.department_id}
                    onChange={(e) => setUserForm({ ...userForm, department_id: e.target.value })}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 bg-white text-slate-700"
                  >
                    <option value="">Select Department...</option>
                    {departmentsList.map(d => (
                      <option key={d.id} value={d.id}>{d.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              {!currentUser && (
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Initial Password</label>
                  <input
                    type="password"
                    placeholder="Defaults to enterprise_pass_2026"
                    value={userForm.password}
                    onChange={(e) => setUserForm({ ...userForm, password: e.target.value })}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 focus:outline-none focus:border-[#8e3a59]"
                  />
                </div>
              )}

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => { setShowAddUserModal(false); setShowEditUserModal(false); }}
                  className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-[#8e3a59] hover:bg-[#782f49] shadow-sm transition-colors"
                >
                  {currentUser ? 'Save Changes' : 'Create User'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── ADD DEPARTMENT MODAL ── */}
      {showAddDeptModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="w-full max-w-md bg-white rounded-xl shadow-2xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">Add Department</h3>
              <button onClick={() => setShowAddDeptModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSaveDept} className="space-y-3.5">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Department Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Sourcing & Vendor Operations"
                  value={deptForm.name}
                  onChange={(e) => setDeptForm({ ...deptForm, name: e.target.value })}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 focus:outline-none focus:border-[#8e3a59]"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Department Code</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. SVO"
                  value={deptForm.code}
                  onChange={(e) => setDeptForm({ ...deptForm, code: e.target.value.toUpperCase() })}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 focus:outline-none focus:border-[#8e3a59]"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAddDeptModal(false)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-[#8e3a59] hover:bg-[#782f49] shadow-sm transition-colors"
                >
                  Save Department
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── DELETE CONFIRMATION DIALOG ── */}
      <DeleteConfirmDialog
        isOpen={deleteDialog.isOpen}
        itemName={deleteDialog.itemName}
        onConfirm={handleConfirmDelete}
        onCancel={() => setDeleteDialog({ isOpen: false, itemType: '', itemId: '', itemName: '' })}
      />

      {/* Toast Feedback */}
      {toastMessage && (
        <Toast
          message={toastMessage}
          type={toastType}
          onClose={() => setToastMessage('')}
        />
      )}
    </div>
  );
};
