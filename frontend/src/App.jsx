import { useState, useEffect } from "react";
import Footer from "./components/Footer";
import NavOption from "./components/NavOption";
import { Link, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";

function App() {
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
  } = useAuth();

  const [showStatus, setShowStatus] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(
    window.matchMedia("(prefers-color-scheme: dark)").matches
  );

  const handleAuthSuccess = (email) => {
    setUserEmail(email);
    navigate("/dashboard/chat")
  };

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const authSuccess = urlParams.get("auth");
    const emailParam = urlParams.get("email");

    if (authSuccess === "success") {
      if (emailParam) setUserEmail(emailParam);
      window.history.replaceState({}, document.title, window.location.pathname);
      navigate("/dashboard/chat")
    }

    if (urlParams.get("salesforce") === "connected") {
      setIsSalesforceConnected(true);
      window.history.replaceState({}, document.title, window.location.pathname);
    }

    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const handleThemeChange = (e) => setIsDarkMode(e.matches);
    mq.addEventListener("change", handleThemeChange);
    return () => mq.removeEventListener("change", handleThemeChange);
  }, []);

  const handleReconnect = () => fetchStatus();
  const handleLogout = async () => {
    await logout();
    navigate("/");
    setShowStatus(false);
    fetchStatus();
  };

  const handleGoogleLogin = () => {
    window.location.href = "http://localhost:8000/login";
  };

  const handleSalesforceLogin = () => {
    if (!isAuthenticated) {
      alert("Please login with Google first");
      return;
    }
    window.location.href = "http://localhost:8000/salesforce/login";
  };

  const handleSalesforceLogout = async () => {
    try {
      await fetch("http://localhost:8000/salesforce/logout", {
        method: "POST",
        credentials: "include"
      });
      setIsSalesforceConnected(false);
      fetchStatus();  // Refresh status
    } catch (error) {
      console.error("Logout error:", error);
    }
  }

  const theme = isDarkMode
    ? {
      bg: "#0a0f1f",
      surface: "#ffffff",
      border: "#1c2a44",
      text: "#d9e6ff",
      subtext: "#8fa8d6",
      buttonBg: "#1f5fbf",
      buttonText: "white",
      navbutton: "#212854",
    }
    : {
      bg: "#e7f1ff",
      surface: "#ffffff",
      border: "#b3cff5",
      text: "#0d2b66",
      subtext: "#3d5fa8",
      buttonBg: "#d8e7ff",
      buttonText: "#0a3aa8",
      navbutton: "#061d42",

    };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        width: "100vw",
        minHeight: "100vh",
        backgroundColor: theme.bg,
        color: theme.text,
      }}
    >
      <nav style={{ position: "fixed", width: "100%", zIndex: 10}}>
        {/* UPPER NAV BAR */}
        <div
          style={{
            flexShrink: 0,
            padding: "12px 20px",
            //borderBottom: `1px solid ${theme.border}`,
            background: theme.bg,
            display: "flex",
            justifyContent: "space_between",
            alignItems: "right",
            width: "100%",
            flexWrap: "wrap",
            //gap: "10px",
            boxSizing: "border-box"
          }}
        >


          {!isAuthenticated ? (
            // LOGGED OUT
            <div className="flex justify-between flex-1 pl-[7.5%]">
              <div style={{ display: "flex", gap: "10px" }}>

                <NavOption label={"Sign In"} target={"login"} theme={theme.text} />

                <NavOption label={"Sign Up"} target={"login"} theme={theme.text} />

                <NavOption label={"Support"} target={"login"} theme={theme.text} />

                <NavOption label={"Contact"} target={"login"} theme={theme.text} />
              </div>
              <Link to="/login">
                <button className="bg-red-500 text-white">Request a Demo</button>
              </Link>
            </div>
          ) : (
            /* LOGGED IN → show your status toggle */
            <div style={{ display: "flex", gap: "10px" }}>

              <NavOption label={"Demo"} target={"login"} theme={theme.text}/>

              <NavOption label={"Support"} target={"login"} theme={theme.text}/>

              <NavOption label={"Contact"} target={"login"} theme={theme.text}/>
            
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
        {/* LOWER NAV BAR */}
        <div
          style={{
            flexShrink: 0,
            padding: "12px 20px",
            borderBottom: `1px solid ${theme.border}`,
            background: theme.surface,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            width: "100%",
            flexWrap: "wrap",
            gap: "10px",
            boxSizing: "border-box",
            fontSize: 25,
          }}
        >
          {/* Left: logo + SECURIVA */}
          <div style={{ display: "flex", alignItems: "center", overflow: "hidden", paddingLeft: 23}}>
            <img
              src="/logo.png"
              alt="SECURIVA Logo"
              style={{
                height: "auto",
                width: "250px",
                objectFit: "cover",
              }}
              onClick={() => navigate("/")}
            />
          </div>

          {/* Right: Login buttons if not authenticated */}
          {!isAuthenticated ? (
            <div style={{ display: "flex", gap: "10px" }}>

              <NavOption label={"Features"} target={"security"} theme={theme.navbutton}/>

              <NavOption label={"Solutions"} target={"agent"} theme={theme.navbutton}/>

              <NavOption label={"Pricing"} target={"pricing"} theme={theme.navbutton}/>
              
              <NavOption label={"About"} target={"login"} theme={theme.navbutton}/>


            </div>
          ) : (
            /* If logged in → show your status toggle */
            <div style={{ display: "flex", gap: "10px" }}>

              <NavOption label={"Features"} target={"security"} theme={theme.navbutton}/>

              <NavOption label={"Solutions"} target={"agent"} theme={theme.navbutton}/>

              <NavOption label={"Pricing"} target={"pricing"} theme={theme.navbutton}/>

              <NavOption label={"Dashboard"} target={"/dashboard"} theme={theme.navbutton}/>
            </div>
          )}

        </div>

        {/* ---------- STATUS SECTION ---------- */}
        {showStatus && (
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
                  onClick={handleGoogleLogin}
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
                  onClick={handleSalesforceLogin}
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
                    onClick={handleSalesforceLogout}
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
              {isAuthenticated && (
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
      </nav>

      {/* ---------- MAIN CONTENT SWITCHER ---------- */}
      <main
        style={{
          width: "100%",
          overflowY: "auto",
          paddingTop: "167.5px",
        }}
      >
        {/* Pass any context used by App.jsx subpages. If used across other routes, elevate to an AuthContext wrapper in main.jsx */}
        <Outlet context={{handleAuthSuccess, handleGoogleLogin, handleSalesforceLogin, isAuthenticated}}/>
        
      </main>

      {/* ---------- FOOTER ---------- */}
      <Footer theme={theme} />
    </div>
  );
}

export default App;
