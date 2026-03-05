import { MessageSquarePlus, Mic, Settings, User, Workflow } from "lucide-react";
import { Link } from "react-router-dom";


const Sidebar = () => {
  return (
    <aside className="flex flex-col h-full w-64 border-r border-gray-300">
      {/* Logo area */}
        <div className="p-4 border-b border-border border-gray-300">
          <img src="logo.png" />
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
      {/* Automations Button */}
        <Link to="/dashboard" className="m-2">
            <button className=" inline-flex justify-normal w-full items-center text-black bg-gray-200 border-gray-300 gap-4 ">
                <Workflow className="w-4 h-4" />
                Automations
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
      </div>
    </aside>
  );
};

export default Sidebar;
