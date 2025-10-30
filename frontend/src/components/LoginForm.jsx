import { useState } from "react";

export default function LoginForm() {
  const [loading, setLoading] = useState(false);

  const handleLogin = () => {
    setLoading(true);

    const url = "http://localhost:8000/login";

    window.location.href = url;
  };

  return (
    <div style={{ maxWidth: "400px", margin: "2rem auto", textAlign: "center" }}>
      <h2>Login</h2>
      <button
        onClick={handleLogin}
        disabled={loading}
        style={{
          width: "100%",
          padding: "10px",
          backgroundColor: "#1976d2",
          color: "white",
          border: "none",
          cursor: "pointer",
        }}
      >
        {loading ? "Redirecting..." : "Login"}
      </button>
      <p style={{ marginTop: "10px", fontSize: "0.9em", color: "#555" }}>
        Clicking Login will redirect you to the backend for authentication.
      </p>
    </div>
  );
}
