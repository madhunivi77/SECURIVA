import { useState, useEffect } from "react";
import ChatBox from "./components/ChatBox";
import LoginForm from "./components/LoginForm";
import Homepage from "./components/Homepage";
import Footer from "./components/Footer";

function App() {
  const [backendStatus, setBackendStatus] = useState("Loading...");
  const [userEmail, setUserEmail] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isSalesforceConnected, setIsSalesforceConnected] = useState(false);
  const [showStatus, setShowStatus] = useState(false);
  const [page, setPage] = useState("home"); 
  const [isDarkMode, setIsDarkMode] = useState(
    window.matchMedia("(prefers-color-scheme: dark)").matches
  );

  const handleAuthSuccess = (email) => {
    setUserEmail(email);
    setPage("chat");
  };

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const authSuccess = urlParams.get("auth");
    const emailParam = urlParams.get("email");

    if (authSuccess === "success") {
      if (emailParam) setUserEmail(emailParam);
      window.history.replaceState({}, document.title, window.location.pathname);
      setPage("chat");
    }

    if (urlParams.get("salesforce") === "connected") {
      setIsSalesforceConnected(true);
      window.history.replaceState({}, document.title, window.location.pathname);
    }

    fetchStatus();

    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const handleThemeChange = (e) => setIsDarkMode(e.matches);
    mq.addEventListener("change", handleThemeChange);
    return () => mq.removeEventListener("change", handleThemeChange);
  }, []);

  const fetchStatus = () => {
    setBackendStatus("Connecting...");
    fetch("http://localhost:8000/api/status", {
      credentials: "include"
    })
      .then((res) => res.json())
      .then((data) => {
        setBackendStatus(`Connected: ${JSON.stringify(data)}`);
        if (data.authenticated !== undefined) setIsAuthenticated(data.authenticated);
        if (data.email) setUserEmail(data.email);
        if (data.salesforce_connected !== undefined) setIsSalesforceConnected(data.salesforce_connected);
      })
      .catch(() => {
        setBackendStatus("❌ Could not connect to backend");
        setIsAuthenticated(false);
      });
  };

  const handleReconnect = () => fetchStatus();
  const handleLogout = async () => {
    try {
      await fetch("http://localhost:8000/api/logout", {
        method: "POST",
        credentials: "include"
      });
      setIsAuthenticated(false);
      setUserEmail(null);
      setIsSalesforceConnected(false);
      setPage("home");
      fetchStatus();
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  const handleGoogleLogin = () => {
    window.location.href = "http://localhost:8000/login";
  };

  const handleSalesforceLogin = () => {
    if (!isAuthenticated) {
      alert("Please login with Google first");
      return;
    }
    window.location.href = "http://localhost:8000/salesforce/login";
  };

  const handleSalesforceLogout = async () => {
    try {
      await fetch("http://localhost:8000/salesforce/logout", {
        method: "POST",
        credentials: "include"
      });
      setIsSalesforceConnected(false);
      fetchStatus();  // Refresh status
    } catch (error) {
      console.error("Logout error:", error);
    }
  }

  const theme = isDarkMode
    ? {
        // ----- DARK MODE (more blue) -----
        bg: "#0a0f1f",            // deep navy blue
        surface: "#11182b",       // richer navy surface
        border: "#1c2a44",        // blue-tinted border
        text: "#d9e6ff",          // soft icy-blue white
        subtext: "#8fa8d6",       // desaturated cool blue
        buttonBg: "#1f5fbf",      // strong blue button
        buttonText: "white",
      }
    : {
        // ----- LIGHT MODE (more blue) -----
        bg: "#e7f1ff",            // pale powder-blue background
        surface: "#ffffff",       // white card surface
        border: "#b3cff5",        // gentle sky-blue border
        text: "#0d2b66",          // deep cobalt text
        subtext: "#3d5fa8",       // cooler muted blue-gray
        buttonBg: "#d8e7ff",      // soft light-blue button
        buttonText: "#0a3aa8",    // bold royal blue text
      };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        width: "100vw",
        minHeight: "100vh",
        backgroundColor: theme.bg,
        color: theme.text,
      }}
    >
      {/* ---------- HEADER ---------- */}
      <header
        style={{
          flexShrink: 0,
          padding: "12px 20px",
          borderBottom: `1px solid ${theme.border}`,
          background: theme.surface,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          width: "100%",
          flexWrap: "wrap",
          gap: "10px",
          boxSizing: "border-box",
        }}
      >
        {/* Left: logo + SECURIVA */}
        <div style={{ display:"flex", alignItems:"center", gap:"10px", overflow:"hidden" }}>
          <img
            src="/logo.png"
            alt="SECURIVA Logo"
            style={{
              height: "32px",
              width: "32px",
              objectFit: "cover",
              borderRadius: "6px",
            }}
          />
          <h1 style={{ margin: 0, fontSize: "1.1rem", whiteSpace:"nowrap" }}>
            SECURIVA
          </h1>
        </div>

        {/* Right: Login buttons if NOT authenticated */}
        {!isAuthenticated ? (
          <div style={{ display: "flex", gap: "10px" }}>
            <button
              onClick={() => setPage("login")}
              style={{
                background: "none",
                border: `1px solid ${theme.border}`,
                color: theme.text,
                borderRadius: "6px",
                padding: "6px 12px",
                cursor: "pointer",
              }}
            >
              Sign In
            </button>

            <button
              onClick={() => setPage("login")}
              style={{
                background: "none",
                border: `1px solid ${theme.border}`,
                color: theme.text,
                borderRadius: "6px",
                padding: "6px 12px",
                cursor: "pointer",
              }}
            >
              Sign Up
            </button>
          </div>
        ) : (
          /* If logged in → show your status toggle */
          <button
            onClick={() => setShowStatus((prev) => !prev)}
            style={{
              background: "none",
              border: `1px solid ${theme.border}`,
              color: theme.subtext,
              borderRadius: "6px",
              padding: "4px 10px",
              cursor: "pointer",
            }}
          >
            {showStatus ? "Hide Status" : "Show Status"}
          </button>
        )}
      </header>

      {/* ---------- STATUS SECTION ---------- */}
      {showStatus && (
        <div
          style={{
            flexShrink: 0,
            background: theme.surface,
            padding: "10px 20px",
            borderBottom: `1px solid ${theme.border}`,
            fontSize: "0.9em",
            color: theme.subtext,
          }}
        >
          <p style={{ margin: "4px 0" }}>{backendStatus}</p>
          <div style={{ display:"flex", flexWrap:"wrap", gap:"8px", marginTop:"8px" }}>
            <button
              onClick={handleReconnect}
              style={{
                background: theme.buttonBg,
                border: "none",
                borderRadius: "6px",
                color: theme.buttonText,
                padding: "6px 12px",
                cursor: "pointer",
              }}
            >
              Reconnect
            </button>

            {!isAuthenticated && (
              <button
                onClick={handleGoogleLogin}
                style={{
                  background: "#4285F4",
                  border: "none",
                  borderRadius: "6px",
                  color: "white",
                  padding: "6px 12px",
                  cursor: "pointer",
                }}
              >
                Login with Google
              </button>
            )}

            {!isSalesforceConnected && isAuthenticated && (
              <button
                onClick={handleSalesforceLogin}
                style={{
                  background: "#00A1E0",
                  border: "none",
                  borderRadius: "6px",
                  color: "white",
                  padding:"6px 12px",
                  cursor:"pointer",
                }}
              >
                Connect Salesforce
              </button>
            )}

            {
              isSalesforceConnected && isAuthenticated && (
                <button
                  onClick={handleSalesforceLogout}
                  style={{
                    background: "#d32f2f",
                    border: "none",
                    borderRadius: "6px",
                    color: "white",
                    padding: "6px 12px",
                    cursor: "pointer",
                    flexShrink: 0,
                }}
                >
                  Disconnect Salesforce
                </button>
              )
            }
            {isAuthenticated && (
              <button
                onClick={handleLogout}
                style={{
                  background: "#d32f2f",
                  border: "none",
                  borderRadius: "6px",
                  color: "white",
                  padding: "6px 12px",
                  cursor: "pointer",
                }}
              >
                Logout
              </button>
            )}
          </div>
        </div>
      )}

      {/* ---------- MAIN CONTENT SWITCHER ---------- */}
      <main
        style={{
          flexGrow: 1,
          display: "flex",
          justifyContent: "center",
          width: "100%",
          overflowY: "auto",
          padding: "1rem 0",
        }}
      >
        <div
          style={{
            width: "100%",
            maxWidth: "1200px",
            height: "100%",
            padding: "0 1rem",
            display: "flex",
            flexDirection: "column",
            justifyContent: "flex-start",
            flexGrow: 1,
          }}
        >
          {page === "home" && (
            <Homepage onLoginClick={() => setPage("login")} />
          )}

          {page === "login" && (
            <LoginForm
              onAuthSuccess={handleAuthSuccess}
              onBack={() => setPage("home")}
              onGoogleLogin={handleGoogleLogin}
              onSalesforceLogin={handleSalesforceLogin}
              isAuthenticated={isAuthenticated}
            />
          )}

          {page === "chat" && (
            <ChatBox userEmail={userEmail} />
          )}
        </div>
      </main>

      {/* ---------- FOOTER ---------- */}
      <Footer theme={theme} />
    </div>
  );
}

export default App;
