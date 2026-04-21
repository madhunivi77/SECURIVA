import { Home, MessageSquare, Mic, Plug, ScrollText, Settings, LogOut } from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const PRIMARY_NAV = [
  { to: "/dashboard", label: "Home", icon: Home, end: true },
  { to: "/dashboard/chat", label: "Chat", icon: MessageSquare },
  { to: "/dashboard/voice", label: "Voice", icon: Mic },
  { to: "/dashboard/logs", label: "Logs", icon: ScrollText },
  { to: "/dashboard/integrations", label: "Integrations", icon: Plug },
];

function itemClass({ isActive }) {
  return [
    "flex items-center gap-2.5 px-2.5 py-1.5 text-sm rounded-md transition-colors",
    isActive
      ? "bg-zinc-100 text-zinc-900 font-medium"
      : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900",
  ].join(" ");
}

export default function Sidebar() {
  const { logout, userEmail } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  return (
    <aside className="w-56 shrink-0 flex flex-col border-r border-zinc-200 bg-white">
      {/* Brand */}
      <div className="px-4 h-14 flex items-center border-b border-zinc-200">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded-sm bg-zinc-900" />
          <span className="text-sm font-semibold tracking-tight text-zinc-900">Securiva</span>
        </div>
      </div>

      {/* Primary nav */}
      <nav className="flex-1 p-2 space-y-0.5 overflow-y-auto">
        {PRIMARY_NAV.map(({ to, label, icon: Icon, end }) => (
          <NavLink key={to} to={to} end={end} className={itemClass}>
            <Icon className="w-4 h-4" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-zinc-200 p-2 space-y-0.5">
        <button
          className="w-full flex items-center gap-2.5 px-2.5 py-1.5 text-sm rounded-md text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900 transition-colors"
        >
          <Settings className="w-4 h-4" />
          <span>Settings</span>
        </button>
        {userEmail && (
          <div className="px-2.5 py-1 text-[11px] text-zinc-500 truncate" title={userEmail}>
            {userEmail}
          </div>
        )}
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-2.5 px-2.5 py-1.5 text-sm rounded-md text-zinc-600 hover:bg-red-50 hover:text-red-600 transition-colors"
        >
          <LogOut className="w-4 h-4" />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
}
