import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import TopBar from "../components/TopBar";
import "../styles/dashboard-theme.css";

const MONO_STACK =
  '"Geist Mono", ui-monospace, SFMono-Regular, "SF Mono", Menlo, monospace';

const Dashboard = () => {
  return (
    <div
      className="sv-theme h-screen w-screen flex overflow-hidden antialiased"
      style={{
        fontFamily: MONO_STACK,
        color: "var(--ink)",
        background:
          "radial-gradient(ellipse 80% 55% at 50% 0%, #0d1330 0%, #05091a 100%)",
      }}
    >
      <Sidebar />
      <div
        className="flex-1 flex flex-col overflow-hidden relative z-[1]"
        style={{ borderLeft: "1px solid var(--border)" }}
      >
        <TopBar />
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
