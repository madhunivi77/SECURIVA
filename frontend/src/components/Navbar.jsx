import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import { useState } from "react";
import NavOption from "./NavOption";
import { Link, useNavigate } from "react-router-dom";
import LanguageSwitcher from "./LanguageSwitcher";
import { useTranslation } from "react-i18next";

export default function Navbar() {
  const [showStatus, setShowStatus] = useState(false);
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

  const {
    theme,
  } = useTheme();

  const handleReconnect = () => fetchStatus();

  const handleLogout = async () => {
    await logout();
    navigate("/");
    setShowStatus(false);
    fetchStatus();
  };

  return (
    <nav className="fixed w-full z-10">
      {/* UPPER NAV BAR */}
      <div
        className="shrink-0 py-3 pb-5 pl-16 px-5 flex justify-between items-center w-full flex-wrap gap-2.5 box-border bg-black"
        style={{
          fontSize: 18
        }}
      >
        {/* Left: logo + SECURIVA */}
        <div style={{ display: "flex", alignItems: "center", overflow: "hidden", paddingLeft: 23, justifyContent: "space-between", flexGrow: 1 }}>
          <img
            src="/LOGO_SECURIVA_FINAL_2.png"
            alt="SECURIVA Logo"
            style={{
              height: "auto",
              width: "250px",
              objectFit: "cover",
            }}
            onClick={() => navigate("/")}
          />

          <div className="flex justify-end p-4 gap-4">
            <LanguageSwitcher />

            <Link to={"/contact"}>
              <button
                className="w-60 h-13.5 bg-red-500 text-white"
              >
                {t("navbar.upper.requestDemo")}
              </button>
            </Link>
          </div>
        </div>


      </div>

      {/* ---------- STATUS SECTION ---------- */}
      {isAuthenticated && showStatus && (
        <div
          style={{
            flexShrink: 0,
            background: theme.surface,
            padding: "10px 20px",
            borderBottom: `1px solid ${theme.border}`,
            fontSize: "0.9em",
            color: theme.subtext,
          }}
        >
          <p style={{ margin: "4px 0" }}>{backendStatus}</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "8px" }}>
            <button
              onClick={handleReconnect}
              style={{
                background: theme.buttonBg,
                border: "none",
                borderRadius: "6px",
                color: theme.buttonText,
                padding: "6px 12px",
                cursor: "pointer",
              }}
            >
              {t("navbar.upper.buttons.reconnect")}
            </button>

            {!isAuthenticated && (
              <button
                onClick={loginGoogle}
                style={{
                  background: "#4285F4",
                  border: "none",
                  borderRadius: "6px",
                  color: "white",
                  padding: "6px 12px",
                  cursor: "pointer",
                }}
              >
                {t("navbar.upper.buttons.loginGoogle")}
              </button>
            )}

            {!isSalesforceConnected && isAuthenticated && (
              <button
                onClick={loginSalesforce}
                style={{
                  background: "#00A1E0",
                  border: "none",
                  borderRadius: "6px",
                  color: "white",
                  padding: "6px 12px",
                  cursor: "pointer",
                }}
              >
                {t("navbar.upper.buttons.connectSalesforce")}
              </button>
            )}

            {
              isSalesforceConnected && isAuthenticated && (
                <button
                  onClick={logoutSalesforce}
                  style={{
                    background: "#d32f2f",
                    border: "none",
                    borderRadius: "6px",
                    color: "white",
                    padding: "6px 12px",
                    cursor: "pointer",
                    flexShrink: 0,
                  }}
                >
                  {t("navbar.upper.buttons.disconnectSalesforce")}
                </button>
              )
            }
            {(
              <button
                onClick={handleLogout}
                style={{
                  background: "#d32f2f",
                  border: "none",
                  borderRadius: "6px",
                  color: "white",
                  padding: "6px 12px",
                  cursor: "pointer",
                }}
              >
                {t("navbar.upper.buttons.logout")}
              </button>
            )}
          </div>
        </div>
      )}

      {/* LOWER NAV BAR */}
      <div
        className="shrink-0 py-3 px-5 flex justify-between w-full flex-wrap box-border  bg-black"
      // style={{ background: theme.bg, }}
      >

        {!isAuthenticated ? (
          // LOGGED OUT
          <div className="flex justify-between flex-1 pl-14">
            <div style={{ display: "flex", gap: "10px" }}>
              <NavOption label={t("navbar.lower.loggedOut.nav.about")} target={"about"} theme={theme.text} />

              <NavOption label={t("navbar.lower.loggedOut.nav.features")} target={"features"} theme={theme.text} />

              <NavOption label={t("navbar.lower.loggedOut.nav.solutions")} target={"solutions"} theme={theme.text} />

              <NavOption label={t("navbar.lower.loggedOut.nav.platform")} target={"platform"} theme={theme.text} />

              <NavOption label={t("navbar.lower.loggedOut.nav.pricing")} target={"pricing"} theme={theme.text} />

              <NavOption label={t("navbar.lower.loggedOut.nav.contact")} target={"contact"} theme={theme.text} />

              <NavOption label={t("navbar.lower.loggedOut.nav.faq")} target={"FAQ"} theme={theme.text} />
            </div>

            <div style={{ display: "flex", gap: "10px" }}>
              <NavOption label={t("navbar.lower.loggedOut.auth.signIn")} target={"provider"} theme={theme.text} />

              <NavOption label={t("navbar.lower.loggedOut.auth.signUp")} target={"signup"} theme={theme.text} />

              <NavOption label={t("navbar.lower.loggedOut.auth.support")} target={"support"} theme={theme.text} />
            </div>
          </div>
        ) : (
          /* LOGGED IN → show your status toggle */
          <div style={{ display: "flex", gap: "10px" }}>

            <NavOption label={t("navbar.lower.loggedIn.nav.about")} target={"about"} theme={theme.text} />

            <NavOption label={t("navbar.lower.loggedIn.nav.features")} target={"features"} theme={theme.text} />

            <NavOption label={t("navbar.lower.loggedIn.nav.support")} target={"support"} theme={theme.text} />

            <NavOption label={t("navbar.lower.loggedIn.nav.contact")} target={"contact"} theme={theme.text} />

            <NavOption label={t("navbar.lower.loggedIn.nav.faq")} target={"FAQ"} theme={theme.text} />

            <NavOption label={t("navbar.lower.loggedIn.nav.dashboard")} target={"dashboard"} theme={theme.text} />
            <button
              onClick={() => setShowStatus((prev) => !prev)}
              style={{
                background: "none",
                //border: `1px solid ${theme.border}`,
                color: theme.border,
                borderRadius: "6px",
                padding: "4px 10px",
                cursor: "pointer",
              }}
            >
              {showStatus ? t("navbar.lower.loggedIn.toggleStatus.hide") : t("navbar.lower.loggedIn.toggleStatus.show")}
            </button>
          </div>
        )}
      </div>
    </nav>
  );
};