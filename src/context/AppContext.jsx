/**
 * RIMBERIO Enterprise Application Context
 * =========================================
 * Manages: authentication state, user profile, permissions,
 * capabilities, navigation, and page routing.
 *
 * NO fake users. NO fake roles. NO hardcoded business data.
 * Everything comes from the backend via JWT-authenticated API calls.
 */
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { RimberioAPI } from '../services/api';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  // ── Navigation State ──
  const [currentPage, setCurrentPage] = useState('landing');
  const [loading, setLoading] = useState(true);

  // ── Auth State ──
  const [user, setUser] = useState(null);
  const [permissions, setPermissions] = useState([]);
  const [capabilities, setCapabilities] = useState([]);
  const [navigation, setNavigation] = useState({ items: [], sections: {} });

  // ── UI State ──
  const [notification, setNotification] = useState({ show: false, message: '' });

  // ── Initialize from stored token ──
  useEffect(() => {
    const token = localStorage.getItem('rimberio_token');
    if (token) {
      loadUserContext().catch(() => {
        // Token invalid/expired
        localStorage.removeItem('rimberio_token');
        localStorage.removeItem('rimberio_user');
        setLoading(false);
      });
    } else {
      setLoading(false);
    }

    // Listen for forced logout (from API 401)
    const handleLogout = () => {
      setUser(null);
      setPermissions([]);
      setCapabilities([]);
      setNavigation({ items: [], sections: {} });
      setCurrentPage('landing');
    };
    window.addEventListener('rimberio_logout', handleLogout);
    return () => window.removeEventListener('rimberio_logout', handleLogout);
  }, []);

  // ── Load full user context from /me endpoints ──
  const loadUserContext = useCallback(async () => {
    try {
      const [meData, permData, capData, navData] = await Promise.all([
        RimberioAPI.getMe(),
        RimberioAPI.getMyPermissions(),
        RimberioAPI.getMyCapabilities(),
        RimberioAPI.getMyNavigation(),
      ]);

      setUser(meData);
      setPermissions(permData.permissions || []);
      setCapabilities(capData.capabilities || []);
      setNavigation({
        items: navData.items || [],
        sections: navData.sections || {},
        role: navData.role,
        role_display: navData.role_display,
      });

      // Navigate to dashboard after context load
      setCurrentPage('dashboard');
    } catch (err) {
      console.error('[AppContext] Failed to load user context:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // ── Login ──
  const login = useCallback(async (email, password) => {
    const result = await RimberioAPI.login(email, password);
    localStorage.setItem('rimberio_token', result.access_token);
    localStorage.setItem('rimberio_user', JSON.stringify(result.user));
    await loadUserContext();
    return result;
  }, [loadUserContext]);

  // ── Register ──
  const register = useCallback(async (data) => {
    const result = await RimberioAPI.register(data);
    localStorage.setItem('rimberio_token', result.access_token);
    await loadUserContext();
    return result;
  }, [loadUserContext]);

  // ── Logout ──
  const logout = useCallback(() => {
    localStorage.removeItem('rimberio_token');
    localStorage.removeItem('rimberio_user');
    setUser(null);
    setPermissions([]);
    setCapabilities([]);
    setNavigation({ items: [], sections: {} });
    setCurrentPage('landing');
  }, []);

  // ── Permission Check Helper ──
  const hasPermission = useCallback(
    (code) => permissions.includes(code),
    [permissions]
  );

  // ── Role Check Helper ──
  const hasRole = useCallback(
    (roleName) => user?.role === roleName || (user?.roles || []).includes(roleName),
    [user]
  );

  return (
    <AppContext.Provider
      value={{
        // Navigation
        currentPage,
        setCurrentPage,
        loading,

        // Auth
        user,
        permissions,
        capabilities,
        navigation,
        login,
        register,
        logout,

        // Helpers
        hasPermission,
        hasRole,

        // UI
        notification,
        setNotification,

        // Reload context (e.g., after admin changes)
        reloadContext: loadUserContext,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => useContext(AppContext);
