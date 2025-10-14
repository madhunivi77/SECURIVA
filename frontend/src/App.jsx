import { useState, useEffect } from "react";
import ChatBox from "./components/ChatBox";

function App() {
  const [backendStatus, setBackendStatus] = useState("Loading...");
  const [authToken, setAuthToken] = useState(null);
  const [csrfToken, setCsrfToken] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Call backend to get status and new token
    // Token will be stored in HTTP-only cookie by backend
    fetchStatus();
  }, []);

  const fetchStatus = () => {
    setBackendStatus("Connecting...");
    fetch("http://localhost:8000/api/status", {
      credentials: "include" // Important: allows cookies to be sent/received
    })
      .then((res) => res.json())
      .then((data) => {
        setBackendStatus(`✅ Connected: ${JSON.stringify(data)}`);

        // Token is stored in HTTP-only cookie by backend
        if (data.authenticated !== undefined) {
          setIsAuthenticated(data.authenticated);
        }
        if (data.token) {
          setAuthToken(data.token);
        }
        if (data.csrf_token) {
          setCsrfToken(data.csrf_token);
        }
      })
      .catch(() => {
        setBackendStatus("❌ Could not connect to backend");
        setIsAuthenticated(false);
      });
  };

  const handleReconnect = () => {
    fetchStatus();
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>React Frontend</h1>

      <h2>Backend Connection Test:</h2>
      {/* <p>{backendStatus}</p> */}
      <p>
        Authentication Status: {isAuthenticated ? "✅ Authenticated" : "❌ Not Authenticated"}
      </p>
      {authToken && (
        <p style={{ fontSize: "0.8em", color: "#666", wordBreak: "break-all" }}>
          Token (first 50 chars): {authToken.substring(0, 50)}...
        </p>
      )}
      <button onClick={handleReconnect} style={{ marginTop: "10px" }}>
        Reconnect
      </button>

      <h2>Chatbox Demo:</h2>
      <ChatBox authToken={authToken} csrfToken={csrfToken} />
    </div>
  );
}

export default App;