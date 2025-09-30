import { useState, useEffect } from "react";

function App() {
  const [status, setStatus] = useState("Loading...");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/status")
      .then((res) => res.json())
      .then((data) => setStatus(JSON.stringify(data)))
      .catch((err) => setStatus("Backend not available"));
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <h1>React Frontend</h1>
      <p>Backend Response: {status}</p>
    </div>
  );
}

export default App;