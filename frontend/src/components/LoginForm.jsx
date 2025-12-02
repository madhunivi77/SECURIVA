import { useState } from "react";

export default function LoginForm({ onAuthSuccess, onBack }) {
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
        credentials: "include",
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Login failed");

      if (data.redirect) {
        window.location.href = data.redirect;
        return;
      }

      onAuthSuccess(email); // notify App
    } catch (err) {
      setMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async () => {

    if (!email || !password) {
      setMessage("You must enter email and password to sign up.");
      return;
    }

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
    window.location.href = "http://localhost:8000/login";
  };

  return (
    <div
      style={{
        maxWidth: "450px",
        margin: "3rem auto",
        padding: "2rem",
        backgroundColor: "#121212",
        color: "white",
        borderRadius: "12px",
        boxShadow: "0 4px 20px rgba(0,0,0,0.4)",
        textAlign: "center",
      }}
    >
      <button
        onClick={onBack}
        style={{
          background: "none",
          border: "none",
          color: "#90caf9",
          cursor: "pointer",
          fontSize: "1rem",
          marginBottom: "1rem",
        }}
      >
        ← Back
      </button>

      <h2 style={{ marginBottom: "1.5rem", color: "#90caf9" }}>Login</h2>

      {/* Email */}
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        style={inputStyle}
      />

      {/* Password */}
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        style={inputStyle}
      />

      {/* Buttons Row */}
      <div style={{ display: "flex", gap: "10px", marginBottom: "15px" }}>
        <button
          onClick={handleLogin}
          disabled={loading}
          style={buttonStyle("#4caf50")}
        >
          {loading ? "Loading..." : "Login"}
        </button>

        <button
          onClick={handleSignup}
          disabled={loading}
          style={buttonStyle("#f57c00")}
        >
          {loading ? "Loading..." : "Sign Up"}
        </button>
      </div>

      {/* Google Login */}
      <button
        onClick={handleGoogleLogin}
        disabled={loading}
        style={buttonStyle("#1976d2", "100%")}
      >
        {loading ? "Redirecting..." : "Login with Google"}
      </button>

      {/* Message */}
      {message && (
        <p
          style={{
            marginTop: "15px",
            fontSize: ".9rem",
            color: message.toLowerCase().includes("success")
              ? "#81c784"
              : "#ef5350",
          }}
        >
          {message}
        </p>
      )}
    </div>
  );
}

/* ----------------- Styles ------------------- */

const inputStyle = {
  width: "100%",
  padding: "10px",
  marginBottom: "12px",
  borderRadius: "6px",
  border: "1px solid #555",
  backgroundColor: "#1e1e1e",
  color: "white",
  boxSizing: "border-box",
};

const buttonStyle = (backgroundColor, width = "100%") => ({
  width,
  padding: "10px",
  backgroundColor,
  color: "white",
  border: "none",
  borderRadius: "6px",
  cursor: "pointer",
});
