// src/pages/AdminNotifications.jsx

import AdminSidebar from "../../components/admin/AdminSidebar";
import {
  Bell,
  AlertTriangle,
  CreditCard,
  ShieldAlert,
  Link,
  Activity,
} from "lucide-react";

export default function AdminNotifications() {

  // -------- MOCK DATA --------
  const notifications = [
    {
      type: "System Alert",
      message: "Server CPU usage exceeded 85%",
      time: "2 min ago",
      icon: AlertTriangle,
      color: "red",
    },
    {
      type: "Payment",
      message: "New subscription payment received",
      time: "10 min ago",
      icon: CreditCard,
      color: "green",
    },
    {
      type: "Security",
      message: "Multiple failed login attempts detected",
      time: "20 min ago",
      icon: ShieldAlert,
      color: "orange",
    },
    {
      type: "Integration",
      message: "Salesforce API connection failed",
      time: "30 min ago",
      icon: Link,
      color: "purple",
    },
    {
      type: "User Activity",
      message: "New user registered",
      time: "1 hr ago",
      icon: Activity,
      color: "blue",
    },
  ];

  return (
    <div className="flex h-screen bg-gray-100 font-sans">

      {/* Sidebar */}
      <AdminSidebar />

      {/* CONTENT */}
      <div className="flex-1 p-6 space-y-6 overflow-y-auto">

        {/* HEADER */}
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-blue-900">
            Notifications Center
          </h1>
          <p className="text-gray-500 text-sm">
            Monitor system alerts, payments, security warnings, and activity updates.
          </p>
        </div>

        {/* ---------------- KPI CARDS ---------------- */}
        <div className="grid grid-cols-4 gap-6">

          <Card
            title="System Alerts"
            value="5"
            subtitle="High priority"
            desc="Critical system performance alerts"
            Icon={AlertTriangle}
            color="red"
          />

          <Card
            title="Payments"
            value="12"
            subtitle="Recent transactions"
            desc="Payment-related notifications"
            Icon={CreditCard}
            color="green"
          />

          <Card
            title="Security Warnings"
            value="3"
            subtitle="Requires review"
            desc="Suspicious activity and threats"
            Icon={ShieldAlert}
            color="orange"
          />

          <Card
            title="User Activity"
            value="18"
            subtitle="Latest updates"
            desc="User actions and engagement"
            Icon={Activity}
            color="blue"
          />

        </div>

        {/* ---------------- NOTIFICATIONS LIST ---------------- */}
        <div className="bg-white p-5 rounded-xl shadow">

          <h2 className="text-sm font-semibold text-blue-900 mb-2">
            Recent Notifications
          </h2>

          <p className="text-xs text-gray-500 mb-4">
            Latest updates across system, payments, security, and integrations.
          </p>

          {notifications.map((n, i) => {
            const Icon = n.icon;

            return (
              <div
                key={i}
                className="flex items-center justify-between mb-4 border-b pb-3"
              >

                {/* LEFT */}
                <div className="flex items-center gap-3">

                  {/* ICON */}
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      colors[n.color]
                    }`}
                  >
                    <Icon size={18} />
                  </div>

                  {/* TEXT */}
                  <div>
                    <p className="text-sm font-medium text-gray-800">
                      {n.message}
                    </p>

                    <p className="text-xs text-gray-400">
                      {n.type}
                    </p>
                  </div>

                </div>

                {/* TIME */}
                <span className="text-xs text-gray-400">
                  {n.time}
                </span>

              </div>
            );
          })}

        </div>

      </div>
    </div>
  );
}


// ---------------- CARD ----------------
const Card = ({ title, value, subtitle, desc, Icon, color }) => {
  const colors = {
    red: "bg-red-100 text-red-600",
    green: "bg-green-100 text-green-600",
    orange: "bg-orange-100 text-orange-600",
    blue: "bg-blue-100 text-blue-600",
  };

  return (
    <div className="bg-white p-5 rounded-xl shadow flex justify-between">

      <div>
        <p className="text-sm text-gray-500">{title}</p>

        <h2 className="text-2xl font-bold text-blue-900 mt-1">
          {value}
        </h2>

        <p className="text-xs text-green-600 mt-1">
          {subtitle}
        </p>

        <p className="text-xs text-gray-400 mt-2 max-w-[200px]">
          {desc}
        </p>
      </div>

      <div className={`w-12 h-12 flex items-center justify-center rounded-full ${colors[color]}`}>
        <Icon size={20} />
      </div>

    </div>
  );
};

// Color mapping (used in list)
const colors = {
  red: "bg-red-100 text-red-600",
  green: "bg-green-100 text-green-600",
  orange: "bg-orange-100 text-orange-600",
  purple: "bg-purple-100 text-purple-600",
  blue: "bg-blue-100 text-blue-600",
};