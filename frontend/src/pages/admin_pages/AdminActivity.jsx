// src/pages/AdminActivity.jsx

import AdminSidebar from "../../components/admin/AdminSidebar";
import {
  Activity,
  User,
  ShieldAlert,
  CreditCard,
  Settings,
} from "lucide-react";

export default function AdminActivity() {

  // -------- MOCK DATA --------
  const logs = [
    {
      type: "Admin Action",
      message: "Admin updated user role",
      user: "admin@system.com",
      time: "2 min ago",
      icon: Settings,
      color: "purple",
    },
    {
      type: "User Change",
      message: "User updated profile information",
      user: "john@example.com",
      time: "10 min ago",
      icon: User,
      color: "blue",
    },
    {
      type: "Payment Update",
      message: "Subscription payment processed",
      user: "lisa@example.com",
      time: "20 min ago",
      icon: CreditCard,
      color: "green",
    },
    {
      type: "API Call",
      message: "OpenAI API request completed",
      user: "system",
      time: "30 min ago",
      icon: Activity,
      color: "orange",
    },
    {
      type: "Security Event",
      message: "Failed login attempt detected",
      user: "unknown",
      time: "1 hr ago",
      icon: ShieldAlert,
      color: "red",
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
            Activity Logs
          </h1>
          <p className="text-gray-500 text-sm">
            Track all system actions including admin changes, user activity, payments, and security events.
          </p>
        </div>

        {/* ---------------- KPI CARDS ---------------- */}
        <div className="grid grid-cols-4 gap-6">

          <Card
            title="Admin Actions"
            value="45"
            subtitle="Recent updates"
            desc="Changes made by administrators"
            Icon={Settings}
            color="purple"
          />

          <Card
            title="User Changes"
            value="120"
            subtitle="Profile updates"
            desc="User activity and account changes"
            Icon={User}
            color="blue"
          />

          <Card
            title="Payments"
            value="32"
            subtitle="Transactions"
            desc="Payment updates and subscriptions"
            Icon={CreditCard}
            color="green"
          />

          <Card
            title="Security Events"
            value="8"
            subtitle="Alerts detected"
            desc="Security-related system events"
            Icon={ShieldAlert}
            color="red"
          />

        </div>

        {/* ---------------- LOG TABLE ---------------- */}
        <div className="bg-white p-5 rounded-xl shadow">

          <h2 className="text-sm font-semibold text-blue-900 mb-2">
            Activity Timeline
          </h2>

          <p className="text-xs text-gray-500 mb-4">
            Chronological log of all system actions and events.
          </p>

          {logs.map((log, i) => {
            const Icon = log.icon;

            return (
              <div
                key={i}
                className="flex items-center justify-between border-b pb-3 mb-3"
              >

                {/* LEFT */}
                <div className="flex items-center gap-3">

                  {/* ICON */}
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center ${colors[log.color]}`}
                  >
                    <Icon size={18} />
                  </div>

                  {/* TEXT */}
                  <div>
                    <p className="text-sm font-medium text-gray-800">
                      {log.message}
                    </p>

                    <p className="text-xs text-gray-400">
                      {log.type} • {log.user}
                    </p>
                  </div>

                </div>

                {/* TIME */}
                <span className="text-xs text-gray-400">
                  {log.time}
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
    purple: "bg-purple-100 text-purple-600",
    blue: "bg-blue-100 text-blue-600",
    green: "bg-green-100 text-green-600",
    red: "bg-red-100 text-red-600",
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


// color mapping
const colors = {
  purple: "bg-purple-100 text-purple-600",
  blue: "bg-blue-100 text-blue-600",
  green: "bg-green-100 text-green-600",
  orange: "bg-orange-100 text-orange-600",
  red: "bg-red-100 text-red-600",
};