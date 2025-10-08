import { useState, useEffect } from "react";
import ChatBox from "./components/ChatBox";

function App() {
  const [backendStatus, setBackendStatus] = useState("Loading...");

  useEffect(() => {
    // Call backend
    fetch("http://127.0.0.1:8000/api/status")
      .then((res) => res.json())
      .then((data) => setBackendStatus(JSON.stringify(data)))
      .catch(() => setBackendStatus("❌ Could not connect to backend"));
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <h1>React Frontend</h1>

      <h2>Backend Connection Test:</h2>
      <p>{backendStatus}</p>

      <h2>Chatbox Demo:</h2>
      <ChatBox />
    </div>
  );
}

export default App;