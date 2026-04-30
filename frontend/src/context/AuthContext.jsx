import { createContext, useContext, useState, useEffect, useCallback } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const LOGOUT_ENDPOINT = "/api/logout";
  const STATUS_ENDPOINT = "/api/status";
  const GOOGLE_LOGIN_ENDPOINT = "/login";
  const SALESFORCE_LOGIN_ENDPOINT = "/salesforce/login";
  const SALESFORCE_LOGOUT_ENDPOINT = "/salesforce/logout";
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userEmail, setUserEmail] = useState(null);
  const [isSalesforceConnected, setIsSalesforceConnected] = useState(false);
  const [backendStatus, setBackendStatus] = useState("Loading...");
  const [loading, setLoading] = useState(true);

  const fetchStatus = useCallback(() => {
    setBackendStatus("Connecting...");
    return fetch(STATUS_ENDPOINT, {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => {
        setBackendStatus(`Connected: ${JSON.stringify(data)}`);
        if (data.authenticated !== undefined) setIsAuthenticated(data.authenticated);
        if (data.email) setUserEmail(data.email);
        if (data.salesforce_connected !== undefined)
          setIsSalesforceConnected(data.salesforce_connected);
        setLoading(false);
        return data;
      })
      .catch(() => {
        setBackendStatus("❌ Could not connect to backend");
        setIsAuthenticated(false);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  const logout = useCallback(async () => {
    try {
      await fetch(LOGOUT_ENDPOINT, {
        method: "POST",
        credentials: "include",
      });
      setIsAuthenticated(false);
      setUserEmail(null);
      setIsSalesforceConnected(false);
    } catch (error) {
      console.error("Logout error:", error);
    }
  }, []);

  const logoutSalesforce = async () => {
    try {
      await fetch(SALESFORCE_LOGOUT_ENDPOINT, {
        method: "POST",
        credentials: "include"
      });
      setIsSalesforceConnected(false);
      fetchStatus();
    } catch (error) {
      console.error("Logout error:", error);
    }
  }

  const loginSalesforce = () => {
    if (!isAuthenticated) {
      alert("Please login with Google first");
      return;
    }
    window.location.href = SALESFORCE_LOGIN_ENDPOINT;
  };

  const loginGoogle = () => {
    window.location.href = GOOGLE_LOGIN_ENDPOINT;
  };

  const value = {
    isAuthenticated,
    userEmail,
    isSalesforceConnected,
    backendStatus,
    loading,
    fetchStatus,
    logout,
    setUserEmail,
    setIsSalesforceConnected,
    loginGoogle,
    loginSalesforce,
    logoutSalesforce
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
