import { HashLink } from 'react-router-hash-link';
import { Link } from 'react-router-dom';
import Copyright from './Copyright';

export default function Footer() {
  const textColor = "#ffffff";

  return (
    <div>
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
          src="/LOGO_SECURIVA_FINAL.png"
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
            grid-template-columns: repeat(4, 1fr);
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


          {/* Features */}
          <div className="sec-footer-col">
            <Link to={"/features"}><h2>Features</h2></Link>
            <ul>
              <li><HashLink smooth scroll={scrollWithOffset} to='/features/#virtual-agent'>Virtual Agent</HashLink></li>
              <li><HashLink smooth scroll={scrollWithOffset} to='/features/#cybersecurity'>Cybersecurity</HashLink></li>
              <li><HashLink smooth scroll={scrollWithOffset} to='/features/#text-agent'>Text Agent</HashLink></li>
              <li><HashLink smooth scroll={scrollWithOffset} to='/features/#vpn'>VPN Secure Access</HashLink></li>
            </ul>
          </div>

          {/* Industries */}
          <div className="sec-footer-col">
            <Link to={"/industries"}><h2>Industries</h2></Link>
            <ul>
              <li><HashLink smooth scroll={scrollWithOffset} to='/industries/#healthcare'>Healthcare</HashLink></li>
              <li><HashLink smooth scroll={scrollWithOffset} to='/industries/#fintech'>Finance &amp; Fintech</HashLink></li>
              <li><HashLink smooth scroll={scrollWithOffset} to='/industries/#ecommerce'>E-commerce</HashLink></li>
              <li><HashLink smooth scroll={scrollWithOffset} to='/industries/#smb'>SMBs</HashLink></li>
              <li><HashLink smooth scroll={scrollWithOffset} to='/industries/#agriculture'>Agriculture</HashLink></li>
              <li><HashLink smooth scroll={scrollWithOffset} to='/industries/#education'>Education</HashLink></li>
              <li><HashLink smooth scroll={scrollWithOffset} to='/industries/#nonprofit'>Non Profit</HashLink></li>
              <li><HashLink smooth scroll={scrollWithOffset} to='/industries/#government'>Government</HashLink></li>
            </ul>
          </div>

          {/* Resources */}
          <div className="sec-footer-col">
            <h2>Resources</h2>
            <ul>
              <li><a href="#">Blog</a></li>
              <li><a href="#">eBooks &amp; Whitepapers</a></li>
              <li><a href="#">Partnerships</a></li>
              <li><a href="#">Media Kit</a></li>
              <li><a href="#">API Documentation</a></li>
              <li>
                <Link to="/admin/login">Admin Login</Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div className="sec-footer-col">
            <h2>Legal</h2>
            <ul>
              <Link to={"/privacy-policy"}><li>Privacy Policy</li></Link>
              <Link to={"/terms-of-service"}><li>Terms of Service</li></Link>
              <Link to={"/data-processing-agreement"}><li>Data Processing Agreement (DPA)</li></Link>
              <Link to={"/cookie-policy"}><li>Cookie Policy</li></Link>
              <Link to={"/security-policy"}><li>Security Policy</li></Link>
              <Link to={"/compliance-overview"}><li>Compliance Overview</li></Link>
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
    </div>
  );
}

// function passed to hash-link scroll prop to offset navbar
export const scrollWithOffset = (el) => {
  const yOffset = -200;
  const y =
    el.getBoundingClientRect().top +
    window.pageYOffset +
    yOffset;

  window.scrollTo({
    top: y,
    behavior: "smooth",
  });
};