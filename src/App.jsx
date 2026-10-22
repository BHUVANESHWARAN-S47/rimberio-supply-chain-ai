import React, { useEffect } from 'react';
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
import { ProductsPage } from './pages/ProductsPage';
import { AdminPage } from './pages/AdminPage';
import { ProcurementOpsPage } from './pages/ProcurementOpsPage';
import { LogisticsOpsPage } from './pages/LogisticsOpsPage';
import { CustomerPortalPage } from './pages/CustomerPortalPage';
import { SupplierPortalPage } from './pages/SupplierPortalPage';

const FULL_SCREEN_PAGES = ['landing', 'login', 'register', 'forgot_password'];

const Inner = () => {
  const { currentPage, setCurrentPage, notification, setNotification, user, navigation } = useApp();

  // Role-Based URL / Page Access Protection: Redirect unauthorized routes to dashboard
  useEffect(() => {
    if (!user || FULL_SCREEN_PAGES.includes(currentPage) || currentPage === 'dashboard') return;

    const allowed = ['dashboard'];
    if (navigation?.sections) {
      Object.values(navigation.sections).forEach((items) => {
        if (Array.isArray(items)) {
          items.forEach((item) => {
            if (item.id) allowed.push(item.id);
          });
        }
      });
    }

    const r = (user.role || '').toUpperCase();
    if (r === 'ADMIN') {
      allowed.push('admin_users', 'admin_departments', 'suppliers', 'products', 'warehouses_carriers', 'ai_agents', 'ai_health', 'audit_logs');
    } else if (r === 'BUYER' || r === 'PROCUREMENT_MANAGER') {
      allowed.push('find_suppliers', 'my_products', 'rfqs', 'negotiations', 'negotiation', 'what_if', 'simulation', 'purchase_orders');
    } else if (r === 'LOGISTICS_MANAGER') {
      allowed.push('shipments', 'carriers', 'warehouses', 'stock', 'delays');
    } else if (r === 'SUPPLIER') {
      allowed.push('my_company', 'my_products', 'rfqs', 'negotiations', 'negotiation', 'orders_to_deliver');
    } else if (r === 'CUSTOMER') {
      allowed.push('my_orders', 'order_tracking', 'notifications', 'support');
    }

    if (!allowed.includes(currentPage)) {
      console.warn(`[RouteGuard] Access blocked for role ${r} to page "${currentPage}". Redirecting to Home.`);
      setCurrentPage('dashboard');
    }
  }, [currentPage, user, navigation, setCurrentPage]);

  const renderPage = () => {
    const isSupplier = user?.role === 'SUPPLIER';

    switch (currentPage) {
      // Auth Pages
      case 'landing':
        return <LandingPage />;
      case 'login':
        return <LoginPage />;
      case 'register':
        return <RegisterPage />;
      case 'forgot_password':
        return <ForgotPasswordPage />;

      // Common Home
      case 'dashboard':
        return <DashboardPage />;

      // Role 1: Admin Pages
      case 'admin_users':
        return <AdminPage initialTab="users" />;
      case 'admin_departments':
        return <AdminPage initialTab="departments" />;
      case 'suppliers':
        return <SupplierPage mode="admin" />;
      case 'products':
        return <ProductsPage mode="admin" />;
      case 'warehouses_carriers':
        return <LogisticsOpsPage initialTab="warehouses" />;
      case 'ai_agents':
        return <AdminPage initialTab="ai" />;
      case 'ai_health':
        return <AdminPage initialTab="health" />;
      case 'audit_logs':
        return <AdminPage initialTab="audit_logs" />;

      // Role 2: Buyer Pages
      case 'find_suppliers':
        return <SupplierPage mode="buyer" />;
      case 'my_products':
        return isSupplier ? (
          <SupplierPortalPage initialTab="products" />
        ) : (
          <ProductsPage mode="buyer" />
        );
      case 'rfqs':
        return isSupplier ? (
          <SupplierPortalPage initialTab="rfqs" />
        ) : (
          <ProcurementOpsPage initialTab="rfqs" />
        );
      case 'negotiation':
      case 'negotiations':
        return <NegotiationPage />;
      case 'simulation':
      case 'what_if':
        return <SimulationPage />;
      case 'purchase_orders':
        return <ProcurementOpsPage initialTab="orders" />;

      // Role 3: Logistics Manager Pages
      case 'shipments':
      case 'deliveries':
        return <LogisticsOpsPage initialTab="shipments" />;
      case 'carriers':
        return <LogisticsOpsPage initialTab="carriers" />;
      case 'warehouses':
        return <LogisticsOpsPage initialTab="warehouses" />;
      case 'stock':
        return <LogisticsOpsPage initialTab="stock" />;
      case 'delays':
        return <LogisticsOpsPage initialTab="delays" />;

      // Role 4: Supplier Pages
      case 'my_company':
        return <SupplierPortalPage initialTab="company" />;
      case 'orders_to_deliver':
        return <SupplierPortalPage initialTab="orders" />;

      // Role 5: Customer Pages
      case 'my_orders':
        return <CustomerPortalPage initialTab="orders" />;
      case 'order_tracking':
        return <CustomerPortalPage initialTab="tracking" />;
      case 'notifications':
        return <CustomerPortalPage initialTab="notifications" />;
      case 'support':
        return <CustomerPortalPage initialTab="support" />;

      default:
        return <DashboardPage />;
    }
  };

  const isFullScreen = FULL_SCREEN_PAGES.includes(currentPage);

  if (isFullScreen) {
    return renderPage();
  }

  return (
    <div className="flex flex-col min-h-screen bg-white text-slate-900">
      <Header />

      {/* Notification Banner */}
      {notification?.show && (
        <div className="rim-notification px-5 py-2.5 flex items-center justify-between border-b border-black/15 bg-amber-50">
          <p className="text-xs font-bold flex-1 mr-2 text-black">
            <span className="font-black text-[#8e3a59]">
              [SYSTEM NOTICE]{' '}
            </span>
            {notification.message}
          </p>
          <button
            onClick={() => setNotification({ show: false })}
            className="text-xs font-black text-black px-2 py-0.5 rounded hover:bg-black/10"
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
