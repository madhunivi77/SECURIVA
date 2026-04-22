// src/components/admin/AdminSidebar.jsx
import {
  Home,
  BarChart3,
  Users,
  CreditCard,
  Link,
  FileText,
  Shield,
  Bell,
  Activity,
  Settings,
  LogOut,
} from "lucide-react";
import { NavLink } from "react-router-dom";

const topMenu = [
  { name: "Dashboard", icon: Home, path: "/admin" },
  { name: "Analytics", icon: BarChart3, path: "/admin/analytics" },
  { name: "Users Analytics", icon: Users, path: "/admin/users" },
  { name: "Payments", icon: CreditCard, path: "/admin/payments" },
  { name: "Integrations", icon: Link, path: "/admin/integrations" },
  { name: "Content Management", icon: FileText, path: "/admin/content" },
  { name: "Cyber Security Track", icon: Shield, path: "/admin/security" },
  { name: "Notifications", icon: Bell, path: "/admin/notifications", badge: 12 },
];

const bottomMenu = [
  { name: "Activity Logs", icon: Activity, path: "/admin/activity" },
  { name: "Settings", icon: Settings, path: "/admin/settings" },
];

const AdminSidebar = () => {
  return (
    <aside className="w-72 min-h-screen bg-gradient-to-b from-[#0B2A4A] to-[#071A2F] text-white flex flex-col px-6 py-8 shadow-xl">
      {/* Header */}
      <div className="mb-10">
      <h2 className="text-xl font-bold leading-tight tracking-tight text-white">
  Admin Panel
</h2>

        <p className="text-slate-300 text-sm mt-2 leading-relaxed">
          Centralized Control for Platform Management, Security, and Operations.
        </p>
      </div>

      {/* Top Navigation */}
      <nav className="space-y-3">
        {topMenu.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.name}
              to={item.path}
              end
              className={({ isActive }) =>
                `flex items-center justify-between px-4 py-3 rounded-xl transition-all duration-200 ${
                  isActive
                    ? "bg-gradient-to-r from-[#2563EB] to-[#1E40AF] text-white shadow-lg"
                    : "bg-white/5 text-white hover:bg-white/10"
                }`
              }
            >
              <div className="flex items-center gap-3">
                <Icon size={18} className="text-white" />
                <span className="text-sm font-medium">{item.name}</span>
              </div>

              {/* Notification Badge */}
              {item.badge && (
                <span className="bg-blue-500 text-white text-xs font-semibold px-2.5 py-1 rounded-full">
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Divider */}
      <div className="border-t border-white/10 my-6"></div>

      {/* Bottom Navigation */}
      <nav className="space-y-3">
        {bottomMenu.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                  isActive
                    ? "bg-gradient-to-r from-[#3B82F6] to-[#2563EB] text-white shadow-lg"
                    : "bg-white/5 text-white hover:bg-white/10"
                }`
              }
            >
              <Icon size={18} className="text-white" />
              <span className="text-sm font-medium">{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Spacer */}
      <div className="flex-1"></div>

      {/* Logout */}
      <NavLink
        to="/logout"
        className="flex items-center gap-3 px-4 py-3 rounded-xl text-white hover:bg-white/10 transition-all duration-200"
      >
        <LogOut size={18} className="text-white" />
        <span className="text-sm font-medium">Log Out</span>
      </NavLink>
    </aside>
  );
};

export default AdminSidebar;