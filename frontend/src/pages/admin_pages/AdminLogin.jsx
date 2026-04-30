import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

export default function AdminLogin() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/admin/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Login failed");
      }

  
      localStorage.setItem("adminToken", data.access_token);

      navigate("/admin");
    } catch (err) {
      setError(err.message || "Invalid credentials");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-login-page">
      <style>{`
        .admin-login-page {
          min-height: 100vh;
          width: 100vw;
          display: flex;
          align-items: center;
          justify-content: center;
          background:
            radial-gradient(circle at top left, rgba(41, 145, 255, 0.35), transparent 35%),
            linear-gradient(135deg, #031633 0%, #052050 45%, #07111f 100%);
          padding: 24px;
          box-sizing: border-box;
        }

        .admin-login-card {
          width: 100%;
          max-width: 440px;
          background: rgba(255, 255, 255, 0.08);
          border: 1px solid rgba(255, 255, 255, 0.16);
          border-radius: 28px;
          padding: 42px 36px;
          box-shadow: 0 28px 80px rgba(0, 0, 0, 0.45);
          backdrop-filter: blur(18px);
        }

        .admin-logo-wrap {
          display: flex;
          justify-content: center;
          margin-bottom: 22px;
        }

        .admin-logo {
          width: 120px;
          height: auto;
          object-fit: contain;
        }

        .admin-login-title {
          color: #ffffff;
          text-align: center;
          font-size: 30px;
          font-weight: 700;
          margin-bottom: 6px;
        }

        .admin-login-subtitle {
          color: rgba(255, 255, 255, 0.68);
          text-align: center;
          font-size: 14px;
          margin-bottom: 28px;
        }

        .admin-field {
          margin-bottom: 18px;
        }

        .admin-field label {
          display: block;
          color: rgba(255, 255, 255, 0.8);
          font-size: 14px;
          margin-bottom: 8px;
        }

        .admin-input {
          width: 100%;
          padding: 14px 15px;
          border-radius: 14px;
          border: 1px solid rgba(255, 255, 255, 0.18);
          outline: none;
          background: rgba(255, 255, 255, 0.12);
          color: white;
          font-size: 15px;
          transition: all 0.2s ease;
        }

        .admin-input::placeholder {
          color: rgba(255, 255, 255, 0.45);
        }

        .admin-input:focus {
          border-color: #2d96ff;
          box-shadow: 0 0 0 3px rgba(45, 150, 255, 0.2);
        }

        .admin-error {
          color: #ff7b7b;
          background: rgba(255, 80, 80, 0.12);
          border: 1px solid rgba(255, 80, 80, 0.25);
          padding: 10px 12px;
          border-radius: 10px;
          font-size: 14px;
          margin-bottom: 14px;
        }

        .admin-login-btn {
          width: 100%;
          padding: 14px;
          border: none;
          border-radius: 16px;
          background: linear-gradient(135deg, #1e90ff, #00b7ff);
          color: white;
          font-size: 16px;
          font-weight: 700;
          cursor: pointer;
          transition: all 0.2s ease;
          box-shadow: 0 14px 30px rgba(30, 144, 255, 0.35);
        }

        .admin-login-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 18px 38px rgba(30, 144, 255, 0.45);
        }

        .admin-login-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .admin-back-link {
          display: block;
          text-align: center;
          margin-top: 20px;
          color: rgba(255, 255, 255, 0.65);
          text-decoration: none;
          font-size: 14px;
        }

        .admin-back-link:hover {
          color: white;
        }
      `}</style>

      <div className="admin-login-card">
        <div className="admin-logo-wrap">
          <img
            src="/LOGO_SECURIVA_FINAL.png"
            alt="SecuriVA Logo"
            className="admin-logo"
          />
        </div>

        <h1 className="admin-login-title">Admin Login</h1>
        <p className="admin-login-subtitle">
          Secure access to SecuriVA Admin Dashboard
        </p>

        <form onSubmit={handleLogin}>
          <div className="admin-field">
            <label>Email</label>
            <input
              type="email"
              className="admin-input"
              placeholder="admin@securiva.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="admin-field">
            <label>Password</label>
            <input
              type="password"
              className="admin-input"
              placeholder="Enter password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && <div className="admin-error">{error}</div>}

          <button className="admin-login-btn" type="submit" disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <Link to="/" className="admin-back-link">
          ← Back to Home
        </Link>
      </div>
    </div>
  );
}