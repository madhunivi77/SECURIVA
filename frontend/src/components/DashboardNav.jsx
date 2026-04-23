import { LogOut, Plus, RotateCcw } from "lucide-react";
import { Link } from "react-router-dom";

export default function DashboardNav ({ onCreateAutomation, onRefresh, heading, subtext }) {
  return (
    <header className="flex items-center justify-between h-16 px-6 border-b border-border border-gray-300">
      <div>
        <h2 className="text-xl font-medium">{heading}</h2>
        <p className="text-md">{subtext}</p>
      </div>

      <div className="flex items-center gap-3">

        {/* Refresh Button */}
        <button className="" onClick={onRefresh}>
          <RotateCcw className="h-4 w-4"/>
        </button>

        {/* New Automation Button */}
        <button className="btn glass-button justify-normal gap-4 m-2">
            <Plus className="w-4 h-4" />
            New Automation
        </button>

        {/* Configure a logout function using auth context provider */}
        <Link to="/">
            <button 
            className="hover:bg-red-300"
            >
            <LogOut className="h-4 w-4" />
            </button>
        </Link>
      </div>
    </header>
  );
};