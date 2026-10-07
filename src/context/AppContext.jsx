import React, { createContext, useContext, useState } from 'react';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  // Navigation flow: landing → login → dashboard
  const [currentPage, setCurrentPage] = useState('landing');

  const [user, setUser] = useState(null);

  const [activeDisruption] = useState({
    id: 'DIS-2026-089',
    title: 'Suez Canal Route Congestion & Port Delay',
    severity: 'CRITICAL',
    impactedSKUs: 42,
    estimatedCostImpact: '$340,000',
    delayDays: 6,
  });

  const [negotiationState, setNegotiationState] = useState({
    round: 4,
    buyerTargetPrice: 142.5,
    supplierAskingPrice: 154.0,
    currentOffer: 148.2,
    agreedLeadTime: '12 Days',
    agentConfidence: 94.8,
  });

  const [notification, setNotification] = useState({
    show: true,
    message:
      'AI Digital Twin active: Autonomous negotiation agent saved $84,200 on Micro-Capacitor batch #772.',
  });

  // Roles defined in research paper & project review slides
  const ROLES = [
    {
      id: 'BUYER_AGENT',
      name: 'Buyer Agent',
      title: 'Enterprise Procurement Lead',
      description: 'Negotiates contracts, sets budget thresholds, enforces enterprise quality.',
      badge: 'BUYER',
    },
    {
      id: 'SUPPLIER_AGENT',
      name: 'Supplier Agent',
      title: 'Vendor Representative (Apex Global)',
      description: 'Offers unit prices, negotiates volume discounts, manages production quotas.',
      badge: 'SUPPLIER',
    },
    {
      id: 'LOGISTICS_AGENT',
      name: 'Logistics Agent',
      title: 'Global Freight & Port Telemetry',
      description: 'Monitors port congestion, carrier transit corridors, and route ETA deltas.',
      badge: 'LOGISTICS',
    },
    {
      id: 'CUSTOMER_IMPACT_AGENT',
      name: 'Customer Impact Agent',
      title: 'Customer Relations & Notification Officer',
      description:
        'Audits order SLAs, delivery impacts, and sends transparent delay notifications.',
      badge: 'CUSTOMER',
    },
    {
      id: 'ADMIN_AUDITOR',
      name: 'Operations Lead',
      title: 'System Auditor & Model Supervisor',
      description: 'Oversees Retain/Negotiate/Switch logic, audits model error & confusion matrix.',
      badge: 'ADMIN',
    },
  ];

  const [currentRole, setCurrentRole] = useState(ROLES[0].id);
  const [customerNoticesCount, setCustomerNoticesCount] = useState(4);
  const [modelLearningMetrics, setModelLearningMetrics] = useState({
    accuracy: '92.4%',
    mae: '0.34 Days',
    rmse: '0.48 Days',
    lastUpdated: 'Just now',
    policyVersion: 'v4.2.1-Adaptive',
  });

  const login = (email, _password) => {
    const name = email
      .split('@')[0]
      .split('.')
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(' ');

    setUser({
      name,
      email,
      role: 'Enterprise Supply Planner',
      company: 'Rimberio Global Dynamics',
      avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=C026D3&color=fff&bold=true&size=64`,
    });
    setCurrentPage('dashboard');
  };

  const logout = () => {
    setUser(null);
    setCurrentPage('landing');
  };

  return (
    <AppContext.Provider
      value={{
        currentPage,
        setCurrentPage,
        user,
        setUser,
        activeDisruption,
        negotiationState,
        setNegotiationState,
        notification,
        setNotification,
        currentRole,
        setCurrentRole,
        roles: ROLES,
        customerNoticesCount,
        setCustomerNoticesCount,
        modelLearningMetrics,
        setModelLearningMetrics,
        login,
        logout,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => useContext(AppContext);
