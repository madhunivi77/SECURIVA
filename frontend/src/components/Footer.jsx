import React from "react";

export default function Footer({ theme = {} }) {
  const textColor = "#ffffff";

  return (
    <footer
      style={{
        background: "#052050", // BLUE main footer
        color: textColor,
        width: "100%",
        flexShrink: 0,
      }}
    >
      <div className="flex justify-center pt-10">
        <img
          src="/LOGO_FOOTER_0000.png"
          alt="Footer Logo"
          className="h-20 object-contain"
        />
      </div>

      <style>{`
        .sec-footer-inner {
          max-width: 1200px;
          margin: 0 auto;
          padding: 40px 20px;
        }

        .sec-footer-grid {
          display: grid;
          grid-template-columns: 1fr;
          gap: 32px;
        }

        @media (min-width: 768px) {
          .sec-footer-grid {
            grid-template-columns: repeat(3, 1fr);
          }
        }

        .sec-footer-col h2 {
          margin-bottom: 12px;
          font-size: 1.05rem;
          font-weight: 600;
        }

        .sec-footer-col ul {
          margin: 0;
          padding-left: 1.1rem;
          line-height: 1.7;
        }

        .sec-footer-col li {
          margin: 6px 0;
        }

        .sec-footer-col a {
          color: rgba(255,255,255,0.8);
          text-decoration: none;
        }

        .sec-footer-col a:hover {
          color: white;
        }

        /* Bottom copyright bar */
        .sec-footer-bottom {
          background: #000;
          color: #ccc;
          padding: 14px 20px;
          font-size: 0.85rem;
        }

        .sec-footer-bottom-inner {
          max-width: 1200px;
          margin: 0 auto;
          display: flex;
          justify-content: space-between;
          flex-wrap: wrap;
          gap: 10px;
        }
      `}</style>

      {/* Main footer */}
      <div className="sec-footer-inner">
        <div className="sec-footer-grid">

          {/* Industries */}
          <div className="sec-footer-col">
            <h2>Industries</h2>
            <ul>
              <li><a href="#">Healthcare</a></li>
              <li><a href="#">Finance &amp; Fintech</a></li>
              <li><a href="#">E-commerce</a></li>
              <li><a href="#">SMBs</a></li>
              <li><a href="#">Agriculture</a></li>
              <li><a href="#">Technology</a></li>
              <li><a href="#">Non Profit</a></li>
              <li><a href="#">Government</a></li>
            </ul>
          </div>

          {/* Resources */}
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

          {/* Legal */}
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

      {/* Black copyright bar */}
      <div className="sec-footer-bottom">
        <div className="sec-footer-bottom-inner">
          <div>
            © 2025 SecuriVA — Powered by Kimuntu Power Inc.
          </div>

          <div>
            Built on AWS Cloud
          </div>
        </div>
      </div>
    </footer>
  );
}
