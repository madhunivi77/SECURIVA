import { useState, useEffect } from "react";
import ChatBox from "./components/ChatBox";

function App() {
  const [backendStatus, setBackendStatus] = useState("Loading...");
  const [authToken, setAuthToken] = useState(null);
  const [csrfToken, setCsrfToken] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showStatus, setShowStatus] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(
    window.matchMedia("(prefers-color-scheme: dark)").matches
  );

  useEffect(() => {
    fetchStatus();

    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const handleThemeChange = (e) => setIsDarkMode(e.matches);
    mq.addEventListener("change", handleThemeChange);
    return () => mq.removeEventListener("change", handleThemeChange);
  }, []);

  const fetchStatus = () => {
    setBackendStatus("Connecting...");
    fetch("http://localhost:8000/api/status", { credentials: "include" })
      .then((res) => res.json())
      .then((data) => {
        setBackendStatus(`✅ Connected: ${JSON.stringify(data)}`);
        if (data.authenticated !== undefined) setIsAuthenticated(data.authenticated);
        if (data.token) setAuthToken(data.token);
        if (data.csrf_token) setCsrfToken(data.csrf_token);
      })
      .catch(() => {
        setBackendStatus("❌ Could not connect to backend");
        setIsAuthenticated(false);
      });
  };

  const handleReconnect = () => fetchStatus();

  const theme = isDarkMode
    ? {
        bg: "#1e1f22",
        surface: "#2a2b31",
        border: "#2f2f2f",
        text: "#e5e5e5",
        subtext: "#aaa",
        buttonBg: "#444",
        buttonText: "white",
      }
    : {
        bg: "#f5f5f5",
        surface: "#ffffff",
        border: "#d0d0d0",
        text: "#222",
        subtext: "#555",
        buttonBg: "#ddd",
        buttonText: "#000",
      };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        width: "100vw",
        height: "100vh",
        backgroundColor: theme.bg,
        color: theme.text,
      }}
    >
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
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
            flexShrink: 1,
            overflow: "hidden",
          }}
        >
          <img
            src="/logo.png"
            alt="SECURIVA Logo"
            style={{
              height: "32px",
              width: "32px",
              objectFit: "cover",
              borderRadius: "6px",
              flexShrink: 0,
            }}
          />
          <h1
            style={{
              margin: 0,
              fontSize: "1.1rem",
              color: theme.text,
              whiteSpace: "nowrap",
              textOverflow: "ellipsis",
              overflow: "hidden",
            }}
          >
            SECURIVA
          </h1>
        </div>

        <button
          onClick={() => setShowStatus((prev) => !prev)}
          style={{
            background: "none",
            border: `1px solid ${theme.border}`,
            color: theme.subtext,
            borderRadius: "6px",
            padding: "4px 10px",
            cursor: "pointer",
            flexShrink: 0,
            whiteSpace: "nowrap",
          }}
        >
          {showStatus ? "Hide Status" : "Show Status"}
        </button>
      </header>

      {showStatus && (
        <div
          style={{
            flexShrink: 0,
            background: theme.surface,
            padding: "10px 20px",
            borderBottom: `1px solid ${theme.border}`,
            fontSize: "0.9em",
            color: theme.subtext,
            width: "100%",
            boxSizing: "border-box",
            display: "flex",
            flexDirection: "column",
            flexWrap: "wrap",
            overflowWrap: "break-word",
          }}
        >
          <p style={{ margin: "4px 0" }}>{backendStatus}</p>
          <p style={{ margin: "4px 0" }}>
            Authentication: {isAuthenticated ? "✅ Authenticated" : "❌ Not Authenticated"}
          </p>
          {authToken && (
            <p style={{ wordBreak: "break-word", margin: "4px 0" }}>
              Token (first 50 chars): {authToken.substring(0, 50)}...
            </p>
          )}
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: "8px",
              marginTop: "8px",
            }}
          >
            <button
              onClick={handleReconnect}
              style={{
                background: theme.buttonBg,
                border: "none",
                borderRadius: "6px",
                color: theme.buttonText,
                padding: "6px 12px",
                cursor: "pointer",
                flexShrink: 0,
              }}
            >
              Reconnect
            </button>
          </div>
        </div>
      )}

      <main
        style={{
          flexGrow: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "flex-start",
          alignItems: "center",
          width: "100%",
          height: "100%",
          overflowY: "auto",
          overflowX: "hidden",
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
          <ChatBox authToken={authToken} csrfToken={csrfToken} />
        </div>
      </main>

      <footer
        style={{
          flexShrink: 0,
          padding: "8px 0",
          textAlign: "center",
          fontSize: "0.8em",
          color: theme.subtext,
          borderTop: `1px solid ${theme.border}`,
          background: theme.surface,
          width: "100%",
        }}
      >
        SECURIVA Chat System © 2025
      </footer>
    </div>
  );
}

export default App;