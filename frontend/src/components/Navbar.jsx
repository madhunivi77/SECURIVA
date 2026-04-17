import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import { useState } from "react";
import NavOption from "./NavOption";
import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const [showStatus, setShowStatus] = useState(false);
  const navigate = useNavigate();
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
    isDarkMode,
    setIsDarkMode,
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

          <Link to={"/contact"}>
            <button
              className="w-50 h-13.5 bg-red-500 text-white"
            >
              Request a Demo
            </button>
          </Link>
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
              Reconnect
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
                Login with Google
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
                Connect Salesforce
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
                  Disconnect Salesforce
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
                Logout
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
              <NavOption label={"About"} target={"about"} theme={theme.text} />

              <NavOption label={"Features"} target={"features"} theme={theme.text} />

              <NavOption label={"Solutions"} target={"solutions"} theme={theme.text} />

              <NavOption label={"Platform"} target={"platform"} theme={theme.text} />

              <NavOption label={"Pricing"} target={"pricing"} theme={theme.text} />

              <NavOption label={"Contact"} target={"contact"} theme={theme.text} />

              <NavOption label={"FAQ"} target={"FAQ"} theme={theme.text} />
            </div>

            <div style={{ display: "flex", gap: "10px" }}>
              <NavOption label={"Sign In"} target={"provider"} theme={theme.text} />

              <NavOption label={"Sign Up"} target={"signup"} theme={theme.text} />

              <NavOption label={"Support"} target={"support"} theme={theme.text} />
            </div>
          </div>
        ) : (
          /* LOGGED IN → show your status toggle */
          <div style={{ display: "flex", gap: "10px" }}>

            <NavOption label={"About"} target={"about"} theme={theme.text} />

            <NavOption label={"Features"} target={"security"} theme={theme.text} />

            <NavOption label={"Support"} target={"support"} theme={theme.text} />

            <NavOption label={"Contact"} target={"contact"} theme={theme.text} />

            <NavOption label={"FAQ"} target={"FAQ"} theme={theme.text} />

            <NavOption label={"Dashboard"} target={"dashboard"} theme={theme.text} />
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
              {showStatus ? "Hide Status" : "Show Status"}
            </button>
          </div>
        )}
      </div>
    </nav>
  );
};