import { useState, useEffect } from "react";
import ChatBox from "./components/ChatBox";

function App() {
  const [backendStatus, setBackendStatus] = useState("Loading...");
  const [authToken, setAuthToken] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if we have a token in localStorage
    const savedToken = localStorage.getItem("auth_token");
    if (savedToken) {
      setAuthToken(savedToken);
      setIsAuthenticated(true);
    }

    // Call backend to get status and new token
    fetchStatus();
  }, []);

  const fetchStatus = () => {
    setBackendStatus("Connecting...");
    fetch("http://127.0.0.1:8000/api/status", {
      credentials: "include" // Important: allows cookies to be sent/received
    })
      .then((res) => res.json())
      .then((data) => {
        setBackendStatus(`✅ Connected: ${JSON.stringify(data)}`);

        // Store token if we received one
        if (data.token) {
          setAuthToken(data.token);
          setIsAuthenticated(data.authenticated);
          localStorage.setItem("auth_token", data.token);
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
      <ChatBox authToken={authToken} />
    </div>
  );
}

export default App;