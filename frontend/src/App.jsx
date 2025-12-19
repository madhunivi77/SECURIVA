import { useState, useEffect } from "react";
import ChatBox from "./components/ChatBox";
import LoginForm from "./components/LoginForm";
import Homepage from "./components/Homepage";
import Footer from "./components/Footer";
import Home_Info from "./components/Home_Info";

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
        bg: "#0a0f1f",            
        surface: "#ffffff",      
        border: "#1c2a44",        
        text: "#d9e6ff",          
        subtext: "#8fa8d6",       
        buttonBg: "#1f5fbf",     
        buttonText: "white",
      }
    : {
        bg: "#e7f1ff",            
        surface: "#ffffff",       
        border: "#b3cff5",        
        text: "#0d2b66",          
        subtext: "#3d5fa8",       
        buttonBg: "#d8e7ff",      
        buttonText: "#0a3aa8",   
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
          //borderBottom: `1px solid ${theme.border}`,
          background: "#b3cff5",
          display: "flex",
          justifyContent: "space_between",
          alignItems: "right",
          width: "100%",
          flexWrap: "wrap",
          //gap: "10px",
          boxSizing: "border-box",
        }}
      >
        

        {/* Right: Login buttons if not authenticated */}
        {!isAuthenticated ? (
          <div style={{ display: "flex", gap: "10px" }}>
            <button
              onClick={() => setPage("login")}
              style={{
                background: "none",
                //border: `1px solid ${theme.border}`,
                color: "#0d2b66",
                borderRadius: "6px",
                padding: "6px 12px",
                cursor: "pointer",
              }}
            >
              Demo
            </button>

            <button
              onClick={() => setPage("login")}
              style={{
                background: "none",
                //border: `1px solid ${theme.border}`,
                color: "#0d2b66",
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
                //border: `1px solid ${theme.border}`,
                color: "#0d2b66",
                borderRadius: "6px",
                padding: "6px 12px",
                cursor: "pointer",
              }}
            >
              Sign Up
            </button>

            <button
              //onClick={() => setPage("login")}
              style={{
                background: "none",
                //border: `1px solid ${theme.border}`,
                color: "#0d2b66",
                borderRadius: "6px",
                padding: "6px 12px",
                cursor: "pointer",
              }}
            >
              Support
            </button>

            <button
              //onClick={() => setPage("login")}
              style={{
                background: "none",
                //border: `1px solid ${theme.border}`,
                color: "#0d2b66",
                borderRadius: "6px",
                padding: "6px 12px",
                cursor: "pointer",
              }}
            >
              Contact
            </button>
          </div>
        ) : (
          /* If logged in → show your status toggle */
          <button
            onClick={() => setShowStatus((prev) => !prev)}
            style={{
              background: "none",
              //border: `1px solid ${theme.border}`,
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
          fontSize: 25,
        }}
      >
        {/* Left: logo + SECURIVA */}
        <div style={{ display:"flex", alignItems:"center", overflow:"hidden" }}>
          <img
            src="/logo.png"
            alt="SECURIVA Logo"
            style={{
              height: "auto",
              width: "250px",
              objectFit: "cover",
            }}
          />
        </div>

        {/* Right: Login buttons if not authenticated */}
        {!isAuthenticated ? (
          <div style={{ display: "flex", gap: "10px" }}>
            <button
              onClick={() => setPage("login")}
              style={{
                background: "none",
                //border: `1px solid ${theme.border}`,
                color: "#0d2b66",
                borderRadius: "6px",
                padding: "6px 12px",
                cursor: "pointer",
              }}
            >
              Features
            </button>

            <button
              onClick={() => setPage("login")}
              style={{
                background: "none",
                //border: `1px solid ${theme.border}`,
                color: "#0d2b66",
                borderRadius: "6px",
                padding: "6px 12px",
                cursor: "pointer",
              }}
            >
              Solutions
            </button>

            <button
              //onClick={() => setPage("login")}
              style={{
                background: "none",
                //border: `1px solid ${theme.border}`,
                color: "#0d2b66",
                borderRadius: "6px",
                padding: "6px 12px",
                cursor: "pointer",
              }}
            >
              Pricing
            </button>

            <button
              //onClick={() => setPage("login")}
              style={{
                background: "none",
                //border: `1px solid ${theme.border}`,
                color: "#0d2b66",
                borderRadius: "6px",
                padding: "6px 12px",
                cursor: "pointer",
              }}
            >
              About
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
            maxWidth: "90%",
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

      <Home_Info theme={theme} />

      {/* ---------- FOOTER ---------- */}
      <Footer theme={theme} />
    </div>
  );
}

export default App;
