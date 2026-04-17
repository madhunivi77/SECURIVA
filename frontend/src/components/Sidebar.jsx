import { LogOut, MessageSquarePlus, Mic, ScrollText, Settings, User } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";


const Sidebar = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  return (
    <aside className="flex flex-col h-full w-64 border-r border-gray-300">
      {/* Logo area */}
        <div className="p-4 border-b border-border border-gray-300">
            <h2 className="text-2xl font-semibold">Automate Flow</h2>
        </div>

      {/* New Chat Button */}
        <Link to="/dashboard/chat" className="m-2">
            <button className=" inline-flex justify-normal w-full items-center text-black bg-gray-200 border-gray-300 gap-4 ">
                <MessageSquarePlus className="w-4 h-4" />
                New Chat
            </button>
        </Link>
      {/* Voice Agent Button */}
        <Link to="/dashboard/voice" className="m-2">
            <button className=" inline-flex justify-normal w-full items-center text-black bg-gray-200 border-gray-300 gap-4 ">
                <Mic className="w-4 h-4" />
                Voice Agent
            </button>
        </Link>

      {/* Logs Button */}
        <Link to="/dashboard/logs" className="m-2">
            <button className=" inline-flex justify-normal w-full items-center text-black bg-gray-200 border-gray-300 gap-4 ">
                <ScrollText className="w-4 h-4" />
                Logs
            </button>
        </Link>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Bottom buttons */}
      <div className="p-4 space-y-2 border-t border-border border-gray-300">
        <button className="inline-flex items-center justify-normal gap-4 m-2">
            <Settings className="w-4 h-4" />
            Settings
        </button>
        <button className="inline-flex items-center justify-normal gap-4 m-2">
            <User className="w-4 h-4" />
            Account
        </button>
        <button onClick={handleLogout} className="inline-flex items-center justify-normal gap-4 m-2 text-red-600 hover:text-red-700">
            <LogOut className="w-4 h-4" />
            Logout
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
