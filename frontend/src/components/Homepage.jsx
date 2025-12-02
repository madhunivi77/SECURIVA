// Homepage.jsx
import React from "react";

export default function Homepage({ onLoginClick }) {
  return (
    <div className="homepage">

      {/* ---------- HEADER ---------- */}
      <header className="hero">

        <div style={{ textAlign: "center", marginBottom: "20px" }}>
          <img
            src="/full_logo.png"
            alt="SecuriVA Full Logo"
            style={{
              width: "260px",
              maxWidth: "90%",
              height: "auto",
              margin: "0 auto",
              display: "block",
            }}
          />
        </div>

        <div className="hero-content">
          <h1>Where AI Intelligence Meets Cybersecurity Excellence</h1>
          <p>
            SecuriVA unifies AI automation, cybersecurity protection, and secure communication
            into one intelligent platform designed for modern enterprises.
          </p>

          <div style={{ margin: "30px 0" }}>
            <video
              src="/home_vid_1.MP4"  
              autoPlay
              loop
              muted
              playsInline
              style={{
                width: "100%",
                maxWidth: "700px",
                borderRadius: "12px",
                display: "block",
                margin: "0 auto",
                boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
              }}
            />
          </div>

          <button onClick={onLoginClick} className="btn btn-primary">
            Get Started
          </button>
        </div>
      </header>

      {/* ---------- KEY SOLUTIONS SECTION ---------- */}
      <section className="solutions-section">
        <h2>🔑 Key Solutions</h2>

        <p>
          SecuriVA is an all-in-one AI-Powered Virtual Assistant Platform that automates,
          protects, and enhances business operations.
        </p>

        <ul>
          <li>
            <strong>AI Virtual Agent:</strong> Streamline workflows, scheduling, and
            communications with smart automation tools.
          </li>
          <li>
            <strong>Cybersecurity Protection:</strong> Real-time AI defense for data,
            users, and digital assets.
          </li>
          <li>
            <strong>AI VPN:</strong> Secure every connection using adaptive, encrypted
            networking.
          </li>
          <li>
            <strong>Customer Interaction:</strong> Manage calls, chats, and emails
            through an intelligent AI avatar.
          </li>
          <li>
            <strong>eBook Generator:</strong> Instantly create training manuals and
            awareness guides.
          </li>
          <li>
            <strong>Integrations:</strong> Connect with Gmail, Microsoft 365,
            Salesforce, OpenAI, and more.
          </li>
        </ul>
      </section>

      {/* ---------- WHY CHOOSE US SECTION ---------- */}
      <section className="why-section">
        <h2>💼 Why Choose SecuriVA</h2>

        <ul>
          <li>
            <strong>All-in-One Platform:</strong> AI automation, cybersecurity, and
            communication in one unified system.
          </li>
          <li>
            <strong>Enterprise-Grade Security:</strong> Built for complete protection
            with encrypted AI-driven systems.
          </li>
          <li>
            <strong>Intelligent & Human-Like:</strong> Engage with a smart,
            conversational AI assistant that adapts to your business.
          </li>
          <li>
            <strong>Seamless Integration:</strong> Works effortlessly with your
            existing tools and cloud services.
          </li>
          <li>
            <strong>Future-Ready:</strong> Powered by AI VPN and Digital Twin
            technology for next-generation innovation.
          </li>
        </ul>
      </section>

    </div>
  );
}
