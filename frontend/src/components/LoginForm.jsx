import { useState } from "react";

export default function LoginForm({ onGoogleLogin, onSalesforceLogin, isAuthenticated = false }) {
  const [loadingGoogle, setLoadingGoogle] = useState(false);
  const [loadingSalesforce, setLoadingSalesforce] = useState(false);

  const handleGoogleLogin = () => {
    setLoadingGoogle(true);
    if (onGoogleLogin) {
      onGoogleLogin();
    } else {
      window.location.href = "http://localhost:8000/login";
    }
  };

  const handleSalesforceLogin = () => {
    setLoadingSalesforce(true);
    if (onSalesforceLogin) {
      onSalesforceLogin();
    } else {
      window.location.href = "http://localhost:8000/salesforce/login";
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "2rem auto", textAlign: "center" }}>
      <h2>Welcome to SECURIVA</h2>
      <p style={{ marginBottom: "1.5rem", color: "#666" }}>
        Sign in to access your account
      </p>

      {/* Google Login Button */}
      <button
        onClick={handleGoogleLogin}
        disabled={loadingGoogle}
        style={{
          width: "100%",
          padding: "12px 20px",
          marginBottom: "12px",
          backgroundColor: "#4285F4",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: loadingGoogle ? "default" : "pointer",
          fontSize: "16px",
          fontWeight: "500",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "12px",
          transition: "background-color 0.2s",
          opacity: loadingGoogle ? 0.7 : 1,
        }}
        onMouseEnter={(e) => {
          if (!loadingGoogle) e.target.style.backgroundColor = "#357ae8";
        }}
        onMouseLeave={(e) => {
          e.target.style.backgroundColor = "#4285F4";
        }}
      >
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M17.64 9.20443C17.64 8.56625 17.5827 7.95262 17.4764 7.36353H9V10.8449H13.8436C13.635 11.9699 13.0009 12.9231 12.0477 13.5613V15.8194H14.9564C16.6582 14.2526 17.64 11.9453 17.64 9.20443Z" fill="white"/>
          <path d="M9 18C11.43 18 13.4673 17.1941 14.9564 15.8195L12.0477 13.5613C11.2418 14.1013 10.2109 14.4204 9 14.4204C6.65591 14.4204 4.67182 12.8372 3.96409 10.71H0.957275V13.0418C2.43818 15.9831 5.48182 18 9 18Z" fill="white"/>
          <path d="M3.96409 10.71C3.78409 10.17 3.68182 9.59318 3.68182 9C3.68182 8.40682 3.78409 7.83 3.96409 7.29V4.95818H0.957275C0.347727 6.17318 0 7.54773 0 9C0 10.4523 0.347727 11.8268 0.957275 13.0418L3.96409 10.71Z" fill="white"/>
          <path d="M9 3.57955C10.3214 3.57955 11.5077 4.03364 12.4405 4.92545L15.0218 2.34409C13.4632 0.891818 11.4259 0 9 0C5.48182 0 2.43818 2.01682 0.957275 4.95818L3.96409 7.29C4.67182 5.16273 6.65591 3.57955 9 3.57955Z" fill="white"/>
        </svg>
        {loadingGoogle ? "Redirecting..." : "Sign in with Google"}
      </button>

      {/* Salesforce Connect Button */}
      <button
        onClick={handleSalesforceLogin}
        disabled={!isAuthenticated || loadingSalesforce}
        style={{
          width: "100%",
          padding: "12px 20px",
          marginBottom: "12px",
          backgroundColor: !isAuthenticated ? "#ccc" : "#00A1E0",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: !isAuthenticated || loadingSalesforce ? "not-allowed" : "pointer",
          fontSize: "16px",
          fontWeight: "500",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "12px",
          transition: "background-color 0.2s",
          opacity: !isAuthenticated || loadingSalesforce ? 0.6 : 1,
        }}
        onMouseEnter={(e) => {
          if (isAuthenticated && !loadingSalesforce) e.target.style.backgroundColor = "#0089c2";
        }}
        onMouseLeave={(e) => {
          if (isAuthenticated) e.target.style.backgroundColor = "#00A1E0";
        }}
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
          <path d="M10.006 5.413a4.74 4.74 0 0 1-.542 3.073 4.73 4.73 0 0 1-2.445 2.066 4.74 4.74 0 0 1 3.088 1.615 4.73 4.73 0 0 1 1.183 3.232v.001-.003c0-1.245-.475-2.445-1.326-3.346a4.7 4.7 0 0 0-3.277-1.406h-.005c1.207-.002 2.364-.48 3.219-1.33a4.72 4.72 0 0 0 1.335-3.23v-.002.003a4.72 4.72 0 0 1 1.336 3.23c0 1.245-.475 2.445-1.327 3.345a4.7 4.7 0 0 1-3.276 1.406h-.005a4.7 4.7 0 0 1 3.277 1.406 4.72 4.72 0 0 1 1.327 3.345v-.002.003a4.72 4.72 0 0 0-1.336-3.231 4.7 4.7 0 0 0-3.218-1.331h-.006a4.7 4.7 0 0 0 3.28 1.406 4.72 4.72 0 0 0 3.343-1.387 4.72 4.72 0 0 0 1.387-3.343v.003-.003a4.72 4.72 0 0 1-1.335 3.23 4.7 4.7 0 0 1-3.219 1.33h-.006c1.207 0 2.364.48 3.218 1.33a4.72 4.72 0 0 1 1.336 3.23v-.001c0-2.61-2.117-4.727-4.727-4.727h-.006c2.61 0 4.727-2.117 4.727-4.727v.001z"/>
        </svg>
        {loadingSalesforce ? "Redirecting..." : "Connect Salesforce"}
      </button>

      {!isAuthenticated && (
        <p style={{ marginTop: "10px", fontSize: "0.85em", color: "#888", fontStyle: "italic" }}>
          Connect Salesforce after signing in with Google
        </p>
      )}

      <p style={{ marginTop: "1.5rem", fontSize: "0.9em", color: "#555" }}>
        You'll be redirected to securely authenticate with your chosen provider.
      </p>
    </div>
  );
}
