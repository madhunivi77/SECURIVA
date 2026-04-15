import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { useEffect, useState } from "react";
import DashboardNav from "../components/DashboardNav";

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
    handleRefresh();
  }, []);
  return (
    <div className="flex h-screen w-screen bg-white text-black">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <DashboardNav onCreateAutomation={handleCreateAutomation} onRefresh={handleRefresh} />

        <main className="flex-1 relative">
          <Outlet context={{handleRefresh, cards:[cards]}}/>
        </main>

      </div>

    </div>
  );
};

export default Dashboard;
