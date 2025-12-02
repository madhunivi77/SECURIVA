import React from "react";

export default function Footer({ theme = {} }) {
  // fallback colors if theme not provided
  const teal = theme.teal || "#0d9488";
  const textColor = theme.subtext || "#6b7280";
  const surface = theme.surface || "#ffffff";
  const border = theme.border || "#e5e7eb";

  const containerStyle = {
    flexShrink: 0,
    padding: "24px 0 8px",
    textAlign: "left",
    fontSize: "0.9rem",
    color: textColor,
    borderTop: `1px solid ${border}`,
    background: surface,
    width: "100%",
    //'--sec-footer-teal' custom property for CSS below
    ["--sec-footer-teal"]: teal,
  };

  return (
    <footer style={containerStyle}>
      {/* Embedded CSS ensures the layout works without Tailwind */}
      <style>{`
        /* Root grid for all columns */
        .sec-footer-inner {
          max-width: 1200px;
          margin: 0 auto;
          padding: 28px 20px;
        }

        .sec-footer-brand {
          text-align: center;
          margin-bottom: 20px;
        }

        .sec-footer-brand h1 {
          margin: 0;
          font-size: 1.6rem;
          font-weight: 700;
          color: var(--sec-footer-teal);
        }

        .sec-footer-grid {
          display: grid;
          grid-template-columns: repeat(1, 1fr);
          gap: 28px;
        }

        /* medium screens: 2 columns */
        @media (min-width: 640px) {
          .sec-footer-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }

        /* large screens: 3 columns across */
        @media (min-width: 1024px) {
          .sec-footer-grid {
            grid-template-columns: repeat(3, 1fr);
          }
        }

        /* Column heading */
        .sec-footer-col h2 {
          margin: 0 0 10px 0;
          font-size: 1rem;
        }

        /* keep items in lists, clickable links */
        .sec-footer-col ul {
          margin: 0;
          padding-left: 1.15rem; /* show bullets */
          line-height: 1.6;
        }

        .sec-footer-col li {
          margin: 6px 0;
        }

        .sec-footer-col a {
          color: inherit;
          text-decoration: none;
          transition: color 140ms ease;
        }

        .sec-footer-col a:hover {
          color: var(--sec-footer-teal);
        }

        /* divider */
        .sec-footer-divider {
          height: 1px;
          background: ${border};
          margin: 20px 0 0;
          width: 100%;
        }

        /* bottom row */
        .sec-footer-bottom {
          max-width: 1200px;
          margin: 18px auto 28px;
          padding: 10px 20px;
          display: flex;
          gap: 12px;
          align-items: center;
          justify-content: space-between;
          flex-wrap: wrap;
          font-size: 0.85rem;
          color: ${textColor};
        }

        .sec-footer-social {
          display: flex;
          gap: 12px;
        }

        .sec-footer-social a {
          color: inherit;
          text-decoration: none;
          padding: 4px;
          border-radius: 6px;
          transition: box-shadow 140ms ease, color 140ms ease;
        }

        .sec-footer-social a:hover {
          color: var(--sec-footer-teal);
          box-shadow: 0 4px 12px rgba(13,148,136,0.12);
        }
      `}</style>

      <div className="sec-footer-inner">
        {/* Branding */}
        <div className="sec-footer-brand" style={{ textAlign: "center" }}>
          <h1 style={{ marginBottom: 6 }}>SecuriVA</h1>
          <div style={{ fontSize: "0.95rem", color: textColor }}>
            Where AI Intelligence Meets Cybersecurity Excellence.
          </div>
        </div>

        {/* GRID containing all 8 columns */}
        <div className="sec-footer-grid" role="navigation" aria-label="Footer">
          {/* 1: Company */}
          <div className="sec-footer-col">
            <h2>Company</h2>
            <ul>
              <li><a href="#">About</a></li>
              <li><a href="#">Ethics &amp; Sustainability</a></li>
              <li><a href="#">Careers</a></li>
              <li><a href="#">Newsroom</a></li>
              <li><a href="#">Leadership</a></li>
              <li><a href="#">Contact</a></li>
              <li><a href="#">Investor Relations</a></li>
            </ul>
          </div>

          {/* 2: Features */}
          <div className="sec-footer-col">
            <h2>Features</h2>
            <ul>
              <li><a href="#">Business Automation</a></li>
              <li style={{ paddingLeft: 12 }}><a href="#">Task automation</a></li>
              <li style={{ paddingLeft: 12 }}><a href="#">AI-powered reporting</a></li>
              <li style={{ paddingLeft: 12 }}><a href="#">Productivity optimization</a></li>

              <li style={{ marginTop: 8 }}><a href="#">Cybersecurity</a></li>
              <li style={{ paddingLeft: 12 }}><a href="#">Phishing detection</a></li>
              <li style={{ paddingLeft: 12 }}><a href="#">Suspicious login alerts</a></li>
              <li style={{ paddingLeft: 12 }}><a href="#">Compliance reminders</a></li>
              <li style={{ paddingLeft: 12 }}><a href="#">Data protection &amp; endpoint security</a></li>

              <li style={{ marginTop: 8 }}><a href="#">Virtual Agent</a></li>
              <li><a href="#">Powered Digital Twin</a></li>
              <li><a href="#">Customer Interaction</a></li>
              <li style={{ paddingLeft: 12 }}><a href="#">Chatbot + Email automation</a></li>
              <li style={{ paddingLeft: 12 }}><a href="#">Voice/video escalation</a></li>
              <li><a href="#">AI VPN</a></li>
              <li><a href="#">Integration Hub</a></li>
            </ul>
          </div>

          {/* 3: Solutions */}
          <div className="sec-footer-col">
            <h2>Solutions</h2>
            <ul>
              <li><a href="#">Enterprise Workflow Automation</a></li>
              <li><a href="#">Intelligent Customer Support</a></li>
              <li><a href="#">Cybersecurity Threat Monitoring</a></li>
              <li><a href="#">Secure Remote Work Enablement</a></li>
              <li><a href="#">AI-Driven Decision Making</a></li>
            </ul>
          </div>

          {/* 4: Platform */}
          <div className="sec-footer-col">
            <h2>Platform</h2>
            <ul>
              <li><a href="#">Hosted on AWS (Amazon Web Services)</a></li>
              <li><a href="#">Built-in AI VPN protection</a></li>
              <li><a href="#">API &amp; SDK Access</a></li>
              <li style={{ marginTop: 8 }}><strong>Integrations:</strong></li>
              <li style={{ paddingLeft: 12 }}><a href="#">Gmail</a></li>
              <li style={{ paddingLeft: 12 }}><a href="#">Google Calendar</a></li>
              <li style={{ paddingLeft: 12 }}><a href="#">Salesforce</a></li>
              <li style={{ paddingLeft: 12 }}><a href="#">WhatsApp</a></li>
              <li style={{ paddingLeft: 12 }}><a href="#">SMS</a></li>
              <li style={{ paddingLeft: 12 }}><a href="#">Microsoft 365</a></li>
              <li style={{ paddingLeft: 12 }}><a href="#">Fintech and banking APIs</a></li>
            </ul>
          </div>

          {/* 5: Industries */}
          <div className="sec-footer-col">
            <h2>Industries</h2>
            <ul>
              <li><a href="#">Healthcare</a></li>
              <li><a href="#">Finance &amp; Fintech</a></li>
              <li><a href="#">E-commerce</a></li>
              <li><a href="#">SMBs</a></li>
              <li><a href="#">Agriculture</a></li>
              <li><a href="#">Technology</a></li>
              <li><a href="#">Non Profit Organization</a></li>
              <li><a href="#">Government</a></li>
            </ul>
          </div>

          {/* 6: Resources */}
          <div className="sec-footer-col">
            <h2>Resources</h2>
            <ul>
              <li><a href="#">Blog</a></li>
              <li><a href="#">eBooks &amp; Whitepapers</a></li>
              <li><a href="#">Affiliates</a></li>
              <li><a href="#">Partnerships</a></li>
              <li><a href="#">Media Kit</a></li>
              <li><a href="#">Webinars</a></li>
              <li><a href="#">API Documentation</a></li>
            </ul>
          </div>

          {/* 7: Support */}
          <div className="sec-footer-col">
            <h2>Support</h2>
            <ul>
              <li><a href="#">Contact Support</a></li>
              <li><a href="#">Help Center</a></li>
              <li><a href="#">FAQs</a></li>
              <li><a href="#">System Status</a></li>
              <li><a href="#">Feedback &amp; Suggestions</a></li>
            </ul>
          </div>

          {/* 8: Legal */}
          <div className="sec-footer-col">
            <h2>Legal</h2>
            <ul>
              <li><a href="#">Privacy Policy</a></li>
              <li><a href="#">Terms of Service</a></li>
              <li><a href="#">Data Protection Policy</a></li>
              <li><a href="#">Cookie Preferences</a></li>
              <li><a href="#">Accessibility Statement</a></li>
            </ul>
          </div>
        </div>
      </div>

      {/* Divider */}
      <div className="sec-footer-divider" />

      {/* Bottom Section */}
      <div className="sec-footer-bottom" aria-hidden="false">
        <div style={{ textAlign: "left" }}>
          © 2025 SecuriVA — Powered by Kimuntu Power Inc.
          <br />
          Built on AWS Cloud
        </div>

        <div className="sec-footer-social" aria-label="Social links">
          <a href="#" aria-label="LinkedIn">LinkedIn</a>
          <a href="#" aria-label="X / Twitter">X</a>
          <a href="#" aria-label="YouTube">YouTube</a>
          <a href="#" aria-label="GitHub">GitHub</a>
          <a href="#" aria-label="Medium">Medium</a>
        </div>
      </div>
    </footer>
  );
}
