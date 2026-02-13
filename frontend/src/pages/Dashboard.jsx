import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import AutomationGrid from "../components/AutomationGrid";

const Dashboard = () => {
  const handleCreateAutomation = () => {
    return;
  };

  return (
    <div className="flex h-screen w-screen bg-white text-black">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Navbar onCreateAutomation={handleCreateAutomation} />

        <main className="flex-1 overflow-auto p-6">
          <AutomationGrid />
        </main>

      </div>
      
    </div>
  );
};

export default Dashboard;
