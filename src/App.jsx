import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';

// Pages
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';
import { DashboardPage } from './pages/DashboardPage';
import { NegotiationPage } from './pages/NegotiationPage';
import { SimulationPage } from './pages/SimulationPage';
import { SupplierPage } from './pages/SupplierPage';
import { DecisionCenterPage } from './pages/DecisionCenterPage';
import { CustomerImpactPage } from './pages/CustomerImpactPage';
import { LearningFeedbackPage } from './pages/LearningFeedbackPage';
import { ReportsPage } from './pages/ReportsPage';

const FULL_SCREEN_PAGES = ['landing', 'login', 'register', 'forgot_password'];

const Inner = () => {
  const { currentPage, notification, setNotification } = useApp();

  const renderPage = () => {
    switch (currentPage) {
      case 'landing':
        return <LandingPage />;
      case 'login':
        return <LoginPage />;
      case 'register':
        return <RegisterPage />;
      case 'forgot_password':
        return <ForgotPasswordPage />;
      case 'dashboard':
        return <DashboardPage />;
      case 'negotiation':
        return <NegotiationPage />;
      case 'simulation':
        return <SimulationPage />;
      case 'suppliers':
        return <SupplierPage />;
      case 'decision_center':
        return <DecisionCenterPage />;
      case 'customer_impact':
        return <CustomerImpactPage />;
      case 'learning_feedback':
        return <LearningFeedbackPage />;
      case 'reports':
        return <ReportsPage />;
      default:
        return <DashboardPage />;
    }
  };

  const isFullScreen = FULL_SCREEN_PAGES.includes(currentPage);

  if (isFullScreen) {
    return renderPage();
  }

  return (
    <div
      className="flex flex-col min-h-screen bg-white text-slate-900"
    >
      <Header />

      {/* Notification Banner */}
      {notification?.show && (
        <div className="rim-notification px-5 py-2.5 flex items-center justify-between border-b border-black/15">
          <p className="text-xs font-bold flex-1 mr-2 text-black" style={{ color: '#000000' }}>
            <span className="font-black" style={{ color: '#000000' }}>
              [AI TWIN EVENT]{' '}
            </span>
            {notification.message}
          </p>
          <button
            onClick={() => setNotification({ show: false })}
            className="text-xs font-black text-black px-2 py-0.5 rounded hover:bg-black/10"
            style={{ color: '#000000' }}
          >
            ✕
          </button>
        </div>
      )}

      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-6 text-black">{renderPage()}</main>
      </div>
    </div>
  );
};

const App = () => (
  <AppProvider>
    <Inner />
  </AppProvider>
);

export default App;
