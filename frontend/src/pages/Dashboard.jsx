import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";

const Dashboard = () => {
  const handleCreateAutomation = () => {
    return;
  };

  return (
    <div className="flex h-screen w-screen bg-white text-black">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Navbar onCreateAutomation={handleCreateAutomation} />

        <main className="flex-1 overflow-auto p-6 relative">
          <Outlet />
        </main>

      </div>

    </div>
  );
};

export default Dashboard;
