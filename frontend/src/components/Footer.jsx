import { HashLink } from 'react-router-hash-link';
import { Link } from 'react-router-dom';
import { useTranslation } from "react-i18next";
import Copyright from './Copyright';

export default function Footer() {
  const { t } = useTranslation();
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
            justify-items: start;
            justify-content: center;
            width: fit-content;
            margin: 0 auto; /* centers the whole block */
          }

          @media (min-width: 768px) {
            .sec-footer-grid {
              grid-template-columns: repeat(2, 2fr);
              justify-items: center;
              width: auto;
            }
          }

          @media (min-width: 1024px) {
            .sec-footer-grid {
              grid-template-columns: repeat(4, 1fr);
              justify-items: center;
              width: auto;
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
              <Link to={"/industries"}>
                <h2>{t("footer.industries.title")}</h2>
              </Link>

              <ul>
                <li>
                  <HashLink smooth scroll={scrollWithOffset} to='/industries/#healthcare'>
                    {t("footer.industries.items.healthcare")}
                  </HashLink>
                </li>

                <li>
                  <HashLink smooth scroll={scrollWithOffset} to='/industries/#fintech'>
                    {t("footer.industries.items.finance")}
                  </HashLink>
                </li>

                <li>
                  <HashLink smooth scroll={scrollWithOffset} to='/industries/#ecommerce'>
                    {t("footer.industries.items.ecommerce")}
                  </HashLink>
                </li>

                <li>
                  <HashLink smooth scroll={scrollWithOffset} to='/industries/#smb'>
                    {t("footer.industries.items.smb")}
                  </HashLink>
                </li>

                <li>
                  <HashLink smooth scroll={scrollWithOffset} to='/industries/#agriculture'>
                    {t("footer.industries.items.agriculture")}
                  </HashLink>
                </li>

                <li>
                  <HashLink smooth scroll={scrollWithOffset} to='/industries/#education'>
                    {t("footer.industries.items.education")}
                  </HashLink>
                </li>

                <li>
                  <HashLink smooth scroll={scrollWithOffset} to='/industries/#nonprofit'>
                    {t("footer.industries.items.nonprofit")}
                  </HashLink>
                </li>

                <li>
                  <HashLink smooth scroll={scrollWithOffset} to='/industries/#government'>
                    {t("footer.industries.items.government")}
                  </HashLink>
                </li>
              </ul>
            </div>

            {/* Resources */}
            <div className="sec-footer-col">
              <h2>{t("footer.resources.title")}</h2>

              <ul>
                <li><a href="#">{t("footer.resources.items.blog")}</a></li>
                <li><a href="#">{t("footer.resources.items.ebooks")}</a></li>
                <li><a href="#">{t("footer.resources.items.affiliates")}</a></li>
                <li><a href="#">{t("footer.resources.items.partnerships")}</a></li>
                <li><a href="#">{t("footer.resources.items.mediaKit")}</a></li>
                <li><a href="#">{t("footer.resources.items.webinars")}</a></li>
                <li><a href="#">{t("footer.resources.items.apiDocs")}</a></li>
              </ul>
            </div>

            {/* Legal */}
            <div className="sec-footer-col">
              <h2>Legal</h2>
              <ul>
                <Link to={"/privacy-policy"}><li>{t("footer.legal.items.privacy")}</li></Link>
                <Link to={"/terms-of-service"}><li>{t("footer.legal.items.terms")}</li></Link>
                <Link to={"/data-processing-agreement"}><li>{t("footer.legal.items.dataProtection")}</li></Link>
                <Link to={"/cookie-policy"}><li>{t("footer.legal.items.cookies")}</li></Link>
                <Link to={"/security-policy"}><li>{t("footer.legal.items.securityPolicy")}</li></Link>
                <Link to={"/compliance-overview"}><li>{t("footer.legal.items.complianceOverview")}</li></Link>
              </ul>
            </div>

          </div>
        </div>

        <Copyright />
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