import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import AutomationGrid from "../components/AutomationGrid";
import { useState, useEffect } from "react";

const Dashboard = () => {

  const [cards, setCards] = useState([]);

  const handleCreateAutomation = async () => {
    return;
  };

  const handleRefresh = async () => {
    // call endpoint
    const res = await fetch("http://localhost:8000/api/dashboard/refresh");
    if(res.status == 200){
      console.log("Data fetched successfully.");
      const data = await res.json();
      setCards(data["cards"]);
    }else{
      console.log("Failed to fetch automation data.")
    }
    return;
  };

  useEffect(() => {
    // Fetch immediately
    handleRefresh();

    // Then poll every 30 seconds
    const interval = setInterval(handleRefresh, 30000);

    // Cleanup when component unmounts
    return () => clearInterval(interval);
  }, [handleRefresh]);

  return (
    <div className="flex h-screen w-screen bg-white text-black">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Navbar onCreateAutomation={handleCreateAutomation} onRefresh={handleRefresh} />

        <main className="flex-1 overflow-auto p-6">
          <AutomationGrid data={cards}/>
        </main>

      </div>
      
    </div>
  );
};

export default Dashboard;
