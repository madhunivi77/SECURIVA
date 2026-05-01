import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import { useState } from "react";
import NavOption from "./NavOption";
import { Link, useNavigate } from "react-router-dom";
import LanguageSwitcher from "./LanguageSwitcher";
import { useTranslation } from "react-i18next";

export default function Navbar() {
  const [showStatus, setShowStatus] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();
  const { t } = useTranslation();

  const {
    isAuthenticated,
    userEmail,
    isSalesforceConnected,
    backendStatus,
    fetchStatus,
    logout,
    setUserEmail,
    setIsSalesforceConnected,
    loginGoogle,
    loginSalesforce,
    logoutSalesforce
  } = useAuth();

  const { theme } = useTheme();

  const handleReconnect = () => fetchStatus();

  const handleLogout = async () => {
    await logout();
    navigate("/");
    setShowStatus(false);
    setMenuOpen(false);
    fetchStatus();
  };

  const closeMenu = () => setMenuOpen(false);

  return (
    <nav className="fixed w-full z-10">
      {/* UPPER NAV BAR */}
      <div className="shrink-0 pt-3 pl-16 pr-5 pb-5 lg:pb-0 flex justify-between items-center w-full flex-wrap gap-2.5 box-border bg-black text-lg">
        <div className="flex items-center overflow-hidden pl-6 justify-between grow">
          <img
            src="/LOGO_SECURIVA_FINAL_2.png"
            alt="SECURIVA Logo"
            className="h-auto w-48 object-cover cursor-pointer"
            onClick={() => navigate("/")}
          />

          {/* Desktop: language switcher + CTA */}
          <div className="hidden md:flex justify-end p-4 gap-4">
            <LanguageSwitcher />
            <Link to={"/contact"}>
              <button className="w-60 h-13.5 bg-red-500 text-white">
                {t("navbar.upper.requestDemo")}
              </button>
            </Link>
          </div>

          {/* Hamburger button (mobile only) */}
          <button
            className="md:hidden flex flex-col justify-center items-center gap-1.5 bg-transparent border-none cursor-pointer p-2 ml-auto"
            onClick={() => setMenuOpen((prev) => !prev)}
            aria-label="Toggle menu"
          >
            <span className={`block w-6 h-0.5 bg-white transition-transform duration-200 ${menuOpen ? "translate-y-2 rotate-45" : ""}`} />
            <span className={`block w-6 h-0.5 bg-white transition-opacity duration-200 ${menuOpen ? "opacity-0" : "opacity-100"}`} />
            <span className={`block w-6 h-0.5 bg-white transition-transform duration-200 ${menuOpen ? "-translate-y-2 -rotate-45" : ""}`} />
          </button>
        </div>
      </div>

      {/* STATUS SECTION */}
      {isAuthenticated && showStatus && (
        <div
          className="shrink-0 px-5 py-2.5 border-b text-sm"
          style={{ background: theme.surface, borderColor: theme.border, color: theme.subtext }}
        >
          <p className="my-1">{backendStatus}</p>
          <div className="flex flex-wrap gap-2 mt-2">
            <button
              onClick={handleReconnect}
              className="border-none rounded-md px-3 py-1.5 cursor-pointer"
              style={{ background: theme.buttonBg, color: theme.buttonText }}
            >
              {t("navbar.upper.buttons.reconnect")}
            </button>
            {!isAuthenticated && (
              <button onClick={loginGoogle} className="border-none rounded-md px-3 py-1.5 cursor-pointer bg-[#4285F4] text-white">
                {t("navbar.upper.buttons.loginGoogle")}
              </button>
            )}
            {!isSalesforceConnected && isAuthenticated && (
              <button onClick={loginSalesforce} className="border-none rounded-md px-3 py-1.5 cursor-pointer bg-[#00A1E0] text-white">
                {t("navbar.upper.buttons.connectSalesforce")}
              </button>
            )}
            {isSalesforceConnected && isAuthenticated && (
              <button onClick={logoutSalesforce} className="border-none rounded-md px-3 py-1.5 cursor-pointer bg-[#d32f2f] text-white shrink-0">
                {t("navbar.upper.buttons.disconnectSalesforce")}
              </button>
            )}
            <button onClick={handleLogout} className="border-none rounded-md px-3 py-1.5 cursor-pointer bg-[#d32f2f] text-white">
              {t("navbar.upper.buttons.logout")}
            </button>
          </div>
        </div>
      )}

      {/* LOWER NAV BAR (desktop only) */}
      <div className="hidden md:flex shrink-0 py-3 px-5 justify-between w-full flex-wrap box-border bg-black">
        {!isAuthenticated ? (
          <div className="flex justify-between flex-1 pl-14">
            <div className="flex gap-2.5">
              <NavOption label={t("navbar.lower.loggedOut.nav.about")} target={"about"} theme={theme.text} />
              <NavOption label={t("navbar.lower.loggedOut.nav.features")} target={"features"} theme={theme.text} />
              <NavOption label={t("navbar.lower.loggedOut.nav.solutions")} target={"solutions"} theme={theme.text} />
              <NavOption label={t("navbar.lower.loggedOut.nav.platform")} target={"platform"} theme={theme.text} />
              <NavOption label={t("navbar.lower.loggedOut.nav.pricing")} target={"pricing"} theme={theme.text} />
              <NavOption label={t("navbar.lower.loggedOut.nav.contact")} target={"contact"} theme={theme.text} />
              <NavOption label={t("navbar.lower.loggedOut.nav.faq")} target={"FAQ"} theme={theme.text} />
            </div>
            <div className="flex gap-2.5">
              <NavOption label={t("navbar.lower.loggedOut.auth.signIn")} target={"provider"} theme={theme.text} />
              <NavOption label={t("navbar.lower.loggedOut.auth.signUp")} target={"signup"} theme={theme.text} />
              <NavOption label={t("navbar.lower.loggedOut.auth.support")} target={"support"} theme={theme.text} />
            </div>
          </div>
        ) : (
          <div className="flex gap-2.5">
            <NavOption label={t("navbar.lower.loggedIn.nav.about")} target={"about"} theme={theme.text} />
            <NavOption label={t("navbar.lower.loggedIn.nav.features")} target={"features"} theme={theme.text} />
            <NavOption label={t("navbar.lower.loggedIn.nav.support")} target={"support"} theme={theme.text} />
            <NavOption label={t("navbar.lower.loggedIn.nav.contact")} target={"contact"} theme={theme.text} />
            <NavOption label={t("navbar.lower.loggedIn.nav.faq")} target={"FAQ"} theme={theme.text} />
            <NavOption label={t("navbar.lower.loggedIn.nav.dashboard")} target={"dashboard"} theme={theme.text} />
            <button
              onClick={() => setShowStatus((prev) => !prev)}
              className="bg-transparent border-none rounded-md px-2.5 py-1 cursor-pointer"
              style={{ color: theme.border }}
            >
              {showStatus ? t("navbar.lower.loggedIn.toggleStatus.hide") : t("navbar.lower.loggedIn.toggleStatus.show")}
            </button>
          </div>
        )}
      </div>

      {/* MOBILE MENU */}
      {menuOpen && (
        <div className="md:hidden flex flex-col w-full bg-black border-t border-[#222] px-6 pt-4 pb-6 gap-2 h-screen">
          {/* Language + CTA */}
          <div className="flex flex-col gap-3 pb-4 border-b border-[#222]">
            <LanguageSwitcher />
            <Link to={"/contact"} onClick={closeMenu}>
              <button className="w-full bg-red-500 text-white py-2.5">
                {t("navbar.upper.requestDemo")}
              </button>
            </Link>
          </div>

          {/* Nav links */}
          <div className="flex flex-col gap-1 pt-2">
            {!isAuthenticated ? (
              <>
                <NavOption label={t("navbar.lower.loggedOut.nav.about")} target={"about"} theme={theme.text} onClick={closeMenu} />
                <NavOption label={t("navbar.lower.loggedOut.nav.features")} target={"features"} theme={theme.text} onClick={closeMenu} />
                <NavOption label={t("navbar.lower.loggedOut.nav.solutions")} target={"solutions"} theme={theme.text} onClick={closeMenu} />
                <NavOption label={t("navbar.lower.loggedOut.nav.platform")} target={"platform"} theme={theme.text} onClick={closeMenu} />
                <NavOption label={t("navbar.lower.loggedOut.nav.pricing")} target={"pricing"} theme={theme.text} onClick={closeMenu} />
                <NavOption label={t("navbar.lower.loggedOut.nav.contact")} target={"contact"} theme={theme.text} onClick={closeMenu} />
                <NavOption label={t("navbar.lower.loggedOut.nav.faq")} target={"FAQ"} theme={theme.text} onClick={closeMenu} />
                <div className="flex flex-col gap-1 mt-2 pt-2 border-t border-[#222]">
                  <NavOption label={t("navbar.lower.loggedOut.auth.signIn")} target={"provider"} theme={theme.text} onClick={closeMenu} />
                  <NavOption label={t("navbar.lower.loggedOut.auth.signUp")} target={"signup"} theme={theme.text} onClick={closeMenu} />
                  <NavOption label={t("navbar.lower.loggedOut.auth.support")} target={"support"} theme={theme.text} onClick={closeMenu} />
                </div>
              </>
            ) : (
              <>
                <NavOption label={t("navbar.lower.loggedIn.nav.about")} target={"about"} theme={theme.text} onClick={closeMenu} />
                <NavOption label={t("navbar.lower.loggedIn.nav.features")} target={"features"} theme={theme.text} onClick={closeMenu} />
                <NavOption label={t("navbar.lower.loggedIn.nav.support")} target={"support"} theme={theme.text} onClick={closeMenu} />
                <NavOption label={t("navbar.lower.loggedIn.nav.contact")} target={"contact"} theme={theme.text} onClick={closeMenu} />
                <NavOption label={t("navbar.lower.loggedIn.nav.faq")} target={"FAQ"} theme={theme.text} onClick={closeMenu} />
                <NavOption label={t("navbar.lower.loggedIn.nav.dashboard")} target={"dashboard"} theme={theme.text} onClick={closeMenu} />
                <button
                  onClick={() => { setShowStatus((prev) => !prev); closeMenu(); }}
                  className="bg-transparent border-none rounded-md px-2.5 py-2 cursor-pointer text-left"
                  style={{ color: theme.border }}
                >
                  {showStatus ? t("navbar.lower.loggedIn.toggleStatus.hide") : t("navbar.lower.loggedIn.toggleStatus.show")}
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
