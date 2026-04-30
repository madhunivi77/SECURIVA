import { useEffect } from "react";
import Footer from "./components/Footer";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import { useTheme } from "./context/ThemeContext";
import Navbar from "./components/Navbar";
import "./i18n";

function App() {
  const {
    setUserEmail,
    setIsSalesforceConnected,
  } = useAuth();

  const {
    theme,
  } = useTheme();

  const navigate = useNavigate();
  const { pathname } = useLocation();

  //Scroll to top on every subpage load
  useEffect(() => {
    if (location.hash) return; // ignore anchor navigation
    window.scrollTo({
      top: 0
    });
  }, [pathname]);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const authStatus = urlParams.get("auth");
    const emailParam = urlParams.get("email");
    const salesforceStatus = urlParams.get("salesforce");

    if (authStatus === "success") {
      if (emailParam) setUserEmail(emailParam);
      window.history.replaceState({}, document.title, window.location.pathname);
      navigate("/dashboard")
    }

    if (salesforceStatus === "connected") {
      setIsSalesforceConnected(true);
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  return (
    <div 
      className="flex flex-col w-screen min-h-screen font-mono"
      style={{
          backgroundColor: theme.bg,
          color: theme.text,
      }}>

      <Navbar />

      {/* ---------- MAIN CONTENT SWITCHER ---------- */}
      <main
        style={{
          width: "100%",
          overflowY: "auto",
          paddingTop: "167.5px",
        }}
      >
        {/* Pass any context used by App.jsx subpages. If used across other routes, elevate to an AuthContext wrapper in main.jsx */}
        <Outlet context={{}}/>
        
      </main>

      {/* ---------- FOOTER ---------- */}
      <Footer />
    </div>
  );
}

export default App;
