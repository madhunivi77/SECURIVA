import { useState } from "react";

export default function LoginForm() {
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [page, setPage] = useState("main"); // "main", "key", or "why"

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

  // ✅ "Back" button handler
  const goBack = () => setPage("main");

  // ✅ Conditionally render based on page
  if (page === "key") {
    return (
      <div
        style={{
          maxWidth: "900px",
          margin: "2rem auto",
          backgroundColor: "#121212",
          color: "#f5f5f5",
          padding: "2rem",
          borderRadius: "12px",
          boxShadow: "0 4px 20px rgba(0,0,0,0.4)",
          textAlign: "left",
        }}
      >
        <h2 style={{ color: "#90caf9", textAlign: "center" }}>🔑 SecuriVA: Key Solutions</h2>
        <p>
          SecuriVA is an AI-Powered Virtual Assistant Platform designed to automate, protect,
          and optimize modern businesses. It merges AI intelligence, cybersecurity, and
          virtual collaboration into one secure ecosystem.
        </p>
        {/* AI Business Automation */}
        <h3 style={{ color: "#81c784" }}>🧠 1. AI Business Automation</h3>
        <ul style={{ textAlign: "left" }}>
          <li>Automate workflows, scheduling, communication, and reporting across your organization.</li>
          <li>Smart task management and workflow optimization.</li>
          <li>Calendar and email synchronization (Gmail, Outlook, etc.).</li>
          <li>Integration with CRMs, project tools, and fintech platforms.</li>
          <li>Auto-generated reports and business summaries.</li>
        </ul>

        {/* Cybersecurity & Data Protection */}
        <h3 style={{ color: "#ffb74d" }}>🔒 2. Cybersecurity & Data Protection</h3>
        <ul style={{ textAlign: "left" }}>
          <li>AI-driven threat detection and prevention.</li>
          <li>Endpoint and cloud protection.</li>
          <li>Identity and access management with biometric analysis.</li>
          <li>Real-time alerts for suspicious behavior or phishing activity.</li>
        </ul>

        {/* AI-Managed VPN */}
        <h3 style={{ color: "#64b5f6" }}>🌐 3. AI-Managed VPN (Secure Connectivity)</h3>
        <ul style={{ textAlign: "left" }}>
          <li>Encrypted communications for calls, emails, and data transfers.</li>
          <li>Dynamic routing for the fastest and safest connections.</li>
          <li>Built-in threat analysis within the VPN layer.</li>
          <li>Compliance with global security standards (GDPR, HIPAA, PCI-DSS).</li>
        </ul>

        {/* Customer Interaction & Communication */}
        <h3 style={{ color: "#ba68c8" }}>🤖 4. Customer Interaction & Communication</h3>
        <ul style={{ textAlign: "left" }}>
          <li>Multichannel assistant: calls, emails, chats, social media, and video.</li>
          <li>AI avatar for customer support and onboarding.</li>
          <li>Personalized follow-ups and smart responses.</li>
          <li>CRM integration for seamless client tracking.</li>
        </ul>

        {/* eBook & Training Content Generation */}
        <h3 style={{ color: "#e57373" }}>📚 5. eBook & Training Content Generation</h3>
        <ul style={{ textAlign: "left" }}>
          <li>Auto-generate professional eBooks and cybersecurity training materials.</li>
          <li>Templates for guides, safety checklists, and onboarding manuals.</li>
          <li>Export options: PDF, EPUB, and web format.</li>
        </ul>
        <p style={{ fontStyle: "italic", color: "#b0bec5" }}>
          Example Outputs: “Cybersecurity for Beginners: Staying Safe Online”, “Data Protection Handbook for Small Businesses”
        </p>

        {/* Cross-Platform Integrations */}
        <h3 style={{ color: "#ffd54f" }}>🧩 6. Cross-Platform Integrations</h3>
        <ul style={{ textAlign: "left" }}>
          <li>Connect SecuriVA with WhatsApp, Gmail, Microsoft 365, Slack, Salesforce, and OpenAI.</li>
          <li>Integrate with financial systems and fintech APIs.</li>
          <li>Build custom integrations using the built-in HTTP request builder.</li>
        </ul>

        {/* AI-Powered Business Digital Twin */}
        <h3 style={{ color: "#ffd54f" }}>🧩 7. AI-Powered Business Digital Twin</h3>
        <ul style={{ textAlign: "left" }}>
          <li>Create a digital replica of your business operations</li>
          <li>Simulate workflows, predict risks, and suggest optimizations</li>
          <li>Identify cyber vulnerabilities before they happen</li>
          <li>Enable predictive decision-making and automated corrections</li>
        </ul>

        <button
          onClick={goBack}
          style={{
            backgroundColor: "#1976d2",
            border: "none",
            color: "white",
            padding: "8px 16px",
            borderRadius: "6px",
            cursor: "pointer",
            display: "block",
            margin: "2rem auto 0",
          }}
        >
          ← Back
        </button>
      </div>
    );
  }

  if (page === "why") {
    return (
      <div
        style={{
          maxWidth: "900px",
          margin: "2rem auto",
          backgroundColor: "#121212",
          color: "#f5f5f5",
          padding: "2rem",
          borderRadius: "12px",
          boxShadow: "0 4px 20px rgba(0,0,0,0.4)",
          textAlign: "left",
        }}
      >
        <h2 style={{ color: "#90caf9", textAlign: "center" }}>💼 Why Choose SecuriVA</h2>
        <p>
          SecuriVA is trusted by organizations worldwide for secure, intelligent, and efficient
          digital transformation. We go beyond automation — empowering teams, protecting data,
          and shaping the future of connected enterprises.
        </p>

        {/* Core Advantages */}
        <h3 style={{ color: "#81c784" }}>🌍 Global Trust & Reliability</h3>
        <ul style={{ textAlign: "left" }}>
          <li>Trusted by enterprises, startups, and government sectors worldwide.</li>
          <li>Proven uptime and reliability backed by AI-driven infrastructure.</li>
          <li>Compliant with international data privacy and security standards.</li>
        </ul>

        <h3 style={{ color: "#f57c00" }}>🧠 AI That Understands You</h3>
        <ul style={{ textAlign: "left" }}>
          <li>Human-like conversations that adapt to tone, intent, and context.</li>
          <li>Personalized experiences across chat, voice, and email.</li>
          <li>Continuous learning from your organization’s knowledge base.</li>
        </ul>

        <h3 style={{ color: "#64b5f6" }}>🔐 Security-First Architecture</h3>
        <ul style={{ textAlign: "left" }}>
          <li>Enterprise-grade encryption and zero-trust access control.</li>
          <li>AI threat prevention and real-time incident detection.</li>
          <li>Isolated virtual environments for sensitive data operations.</li>
        </ul>

        <h3 style={{ color: "#ba68c8" }}>⚙️ Seamless Integrations</h3>
        <ul style={{ textAlign: "left" }}>
          <li>Integrates effortlessly with Gmail, Microsoft 365, Slack, Salesforce, and APIs.</li>
          <li>Customizable workflows for your existing business tools.</li>
          <li>Supports CRM, analytics, and communication ecosystems.</li>
        </ul>

        <h3 style={{ color: "#e57373" }}>🚀 Future-Proof Technology</h3>
        <ul style={{ textAlign: "left" }}>
          <li>Backed by AI VPN, digital twin systems, and autonomous AI infrastructure.</li>
          <li>Regular updates for evolving cybersecurity and compliance frameworks.</li>
          <li>Innovation roadmap aligned with global enterprise trends.</li>
        </ul>

        <p style={{ fontStyle: "italic", color: "#b0bec5" }}>
          “Choose SecuriVA — where intelligent automation meets uncompromising security.”
        </p>
        <button
          onClick={goBack}
          style={{
            backgroundColor: "#1976d2",
            border: "none",
            color: "white",
            padding: "8px 16px",
            borderRadius: "6px",
            cursor: "pointer",
            display: "block",
            margin: "2rem auto 0",
          }}
        >
          ← Back
        </button>
      </div>
    );
  }

  // ✅ Default "main" login + cards view
  return (
    <div
      style={{
        maxWidth: "1000px",
        margin: "2rem auto",
        textAlign: "center",
        boxSizing: "border-box",
        backgroundColor: "#121212",
        color: "#f5f5f5",
        padding: "2rem",
        borderRadius: "12px",
        boxShadow: "0 4px 20px rgba(0, 0, 0, 0.4)",
      }}
    >
      <h2 style={{ color: "#90caf9" }}>SecuriVA</h2>

      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        style={{
          width: "100%",
          boxSizing: "border-box",
          padding: "10px",
          marginBottom: "10px",
          borderRadius: "6px",
          border: "1px solid #555",
          backgroundColor: "#1e1e1e",
          color: "white",
        }}
      />

      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        style={{
          width: "100%",
          boxSizing: "border-box",
          padding: "10px",
          marginBottom: "20px",
          borderRadius: "6px",
          border: "1px solid #555",
          backgroundColor: "#1e1e1e",
          color: "white",
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
            borderRadius: "6px",
            cursor: "pointer",
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
            borderRadius: "6px",
            cursor: "pointer",
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
          borderRadius: "6px",
          cursor: "pointer",
        }}
      >
        {loading ? "Redirecting..." : "Login with Google"}
      </button>

      {message && (
        <p
          style={{
            marginTop: "10px",
            fontSize: "0.9em",
            color: message.includes("success") ? "#81c784" : "#ef5350",
          }}
        >
          {message}
        </p>
      )}

      {/* Info sections side-by-side */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "stretch",
          gap: "20px",
          marginTop: "2.5rem",
          flexWrap: "nowrap",
        }}
      >
        {/* Key Solutions Card */}
        <div
          style={{
            backgroundColor: "#1e1e1e",
            color: "white",
            padding: "20px",
            borderRadius: "8px",
            flex: 1,
            minWidth: "300px",
            boxSizing: "border-box",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <h3 style={{ margin: 0 }}>🔑 Key Solutions</h3>
            <button
              style={{
                backgroundColor: "#1976d2",
                border: "none",
                color: "white",
                padding: "6px 12px",
                borderRadius: "4px",
                cursor: "pointer",
              }}
              onClick={() => setPage("key")}
            >
              See More
            </button>
          </div>

          <p>
            SecuriVA is an all-in-one AI-Powered Virtual Assistant Platform that automates, protects, and enhances business operations.
          </p>
          <ul style={{ textAlign: "left" }}>
            <li>AI Virtual Agent : Streamline workflows, scheduling, and communications with smart automation tools.</li>
            <li>Cybersecurity Protection : Real-time AI defense for data, users, and digital assets.</li>
            <li>AI VPN : Secure every connection with adaptive, encrypted networking.</li>
            <li>Customer Interaction : Manage calls, chats, and emails through an intelligent AI avatar.</li>
            <li>eBook Generator : Instantly create training manuals and awareness guides.</li>
            <li>Integrations : Connect with Gmail, Microsoft 365, Salesforce, OpenAI, and more.</li>
          </ul>
        </div>

        {/* Why Choose SecuriVA Card */}
        <div
          style={{
            backgroundColor: "#1e1e1e",
            color: "white",
            padding: "20px",
            borderRadius: "8px",
            flex: 1,
            minWidth: "300px",
            boxSizing: "border-box",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <h3 style={{ margin: 0 }}>💼 Why Choose SecuriVA</h3>
            <button
              style={{
                backgroundColor: "#1976d2",
                border: "none",
                color: "white",
                padding: "6px 12px",
                borderRadius: "4px",
                cursor: "pointer",
              }}
              onClick={() => setPage("why")}
            >
              See More
            </button>
          </div>

          <ul style={{ textAlign: "left" }}>
            <li>All-in-One Platform: Combines AI automation, cybersecurity, and communication in one secure hub.</li>
            <li>Enterprise-Grade Security: Built for total protection with encrypted AI-driven systems.</li>
            <li>Intelligent & Human-Like: Engage with a smart, conversational AI assistant that understands your business.</li>
            <li>Seamless Integration: Works effortlessly across your existing tools and cloud services.</li>
            <li>Future-Ready: Powered by innovation : including AI VPN and Digital Twin technology.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
