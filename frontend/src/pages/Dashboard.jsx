import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { useState, useEffect } from "react";

const Dashboard = () => {

  const [cards, setCards] = useState([]);

  const handleCreateAutomation = async () => {
    return;
  };

  const handleRefresh = async () => {
    // call endpoint
    const res = await fetch("/api/dashboard/refresh");
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
    handleRefresh();
    const interval = setInterval(handleRefresh, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex h-screen w-screen bg-white text-black">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <main className="flex-1 overflow-auto p-6 relative">
          <Outlet />
        </main>
      </div>

    </div>
  );
};

export default Dashboard;
