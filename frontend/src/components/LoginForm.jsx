import { useState } from "react";

export default function LoginForm() {
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleLogin = async () => {
    setLoading(true);
    setMessage("");

    try {
      const response = await fetch("http://localhost:8000/login/manual", {
        method: "POST",
        body: new URLSearchParams({ email, password }),
        credentials: "include", // include cookies like auth_token
      });

      const data = await response.json();

      if (!response.ok) throw new Error(data.error || "Login failed");

      // ✅ If backend returns redirect URL, navigate there
      if (data.redirect) {
        window.location.href = data.redirect;
      } else {
        setMessage(data.message || "Login successful");
      }
    } catch (err) {
      setMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async () => {
    setLoading(true);
    setMessage("");

    try {
      const response = await fetch("http://localhost:8000/signup", {
        method: "POST",
        body: new URLSearchParams({ email, password }),
        credentials: "include",
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Signup failed");
      setMessage(data.message);
    } catch (err) {
      setMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    const url = "http://localhost:8000/login";
    window.location.href = url;
  };

  return (
    <div
      style={{
        maxWidth: "400px",
        margin: "2rem auto",
        textAlign: "center",
        boxSizing: "border-box",
      }}
    >
      <h2>Login</h2>

      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        style={{
          width: "100%",
          padding: "10px",
          marginBottom: "10px",
          borderRadius: "4px",
          border: "1px solid #ccc",
          boxSizing: "border-box",
        }}
      />

      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        style={{
          width: "100%",
          padding: "10px",
          marginBottom: "20px",
          borderRadius: "4px",
          border: "1px solid #ccc",
          boxSizing: "border-box",
        }}
      />

      <div style={{ display: "flex", gap: "10px", marginBottom: "15px" }}>
        <button
          onClick={handleLogin}
          disabled={loading}
          style={{
            flex: 1,
            padding: "10px",
            backgroundColor: "#4caf50",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            boxSizing: "border-box",
          }}
        >
          {loading ? "Please wait..." : "Login"}
        </button>

        <button
          onClick={handleSignup}
          disabled={loading}
          style={{
            flex: 1,
            padding: "10px",
            backgroundColor: "#f57c00",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            boxSizing: "border-box",
          }}
        >
          {loading ? "Please wait..." : "Signup"}
        </button>
      </div>

      <button
        onClick={handleGoogleLogin}
        disabled={loading}
        style={{
          width: "100%",
          padding: "10px",
          backgroundColor: "#1976d2",
          color: "white",
          border: "none",
          cursor: "pointer",
          boxSizing: "border-box",
        }}
      >
        {loading ? "Redirecting..." : "Login with Google"}
      </button>

      {message && (
        <p
          style={{
            marginTop: "10px",
            fontSize: "0.9em",
            color: message.includes("success") ? "green" : "red",
          }}
        >
          {message}
        </p>
      )}
    </div>
  );
}
