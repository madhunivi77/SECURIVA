// src/pages/AdminIntegrations.jsx

import AdminSidebar from "../../components/admin/AdminSidebar";
import {
  Plug,
  Link,
  Key,
  Activity,
  CheckCircle,
  XCircle,
} from "lucide-react";

export default function AdminIntegrations() {

  // -------- MOCK DATA --------
  const integrations = [
    { name: "WhatsApp", status: "Connected" },
    { name: "Gmail", status: "Connected" },
    { name: "Salesforce", status: "Disconnected" },
    { name: "Microsoft", status: "Connected" },
    { name: "Banking APIs", status: "Disconnected" },
    { name: "OpenAI", status: "Connected" },
    { name: "AWS", status: "Connected" },
    { name: "Azure", status: "Disconnected" },
    { name: "Google Cloud", status: "Connected" },
  ];

  const apiLogs = [
    { api: "OpenAI", action: "Request Sent", status: "Success", time: "2 min ago" },
    { api: "Gmail", action: "Email Sync", status: "Success", time: "10 min ago" },
    { api: "Salesforce", action: "Data Fetch", status: "Failed", time: "30 min ago" },
  ];

  return (
    <div className="flex h-screen bg-gray-100 font-sans">

      

      {/* Content */}
      <div className="flex-1 p-6 space-y-6 overflow-y-auto">

        {/* HEADER */}
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-blue-900">
            Integrations
          </h1>
          <p className="text-gray-500 text-sm">
            Manage external platform connections and API integrations.
          </p>
        </div>

        {/* ---------------- KPI CARDS ---------------- */}
        <div className="grid grid-cols-4 gap-6">

          <Card
            title="Active Integrations"
            value="6"
            subtitle="Connected APIs"
            desc="Total number of active external integrations"
            Icon={Plug}
            color="blue"
          />

          <Card
            title="API Keys"
            value="12"
            subtitle="Stored securely"
            desc="Number of API keys configured in the system"
            Icon={Key}
            color="green"
          />

          <Card
            title="API Calls"
            value="8,540"
            subtitle="Last 24 hours"
            desc="Total API requests made across integrations"
            Icon={Activity}
            color="purple"
          />

          <Card
            title="Failed Calls"
            value="3"
            subtitle="Needs attention"
            desc="Failed API requests requiring investigation"
            Icon={XCircle}
            color="red"
          />

        </div>

        {/* ---------------- AVAILABLE INTEGRATIONS ---------------- */}
        <div className="bg-white p-5 rounded-xl shadow">
          <h2 className="text-sm font-semibold text-blue-900 mb-2">
            Available Integrations
          </h2>

          <p className="text-xs text-gray-500 mb-4">
            Connect and manage third-party platforms.
          </p>

          <div className="grid grid-cols-3 gap-4">

            {integrations.map((int, i) => (
              <div
                key={i}
                className="border rounded-lg p-4 flex justify-between items-center"
              >
                <div>
                  <p className="text-sm font-medium text-gray-800">
                    {int.name}
                  </p>

                  <p
                    className={`text-xs ${
                      int.status === "Connected"
                        ? "text-green-600"
                        : "text-gray-400"
                    }`}
                  >
                    {int.status}
                  </p>
                </div>

                <button
                  className={`px-3 py-1 text-xs rounded-lg ${
                    int.status === "Connected"
                      ? "bg-red-100 text-red-600"
                      : "bg-blue-100 text-blue-600"
                  }`}
                >
                  {int.status === "Connected" ? "Disconnect" : "Connect"}
                </button>
              </div>
            ))}

          </div>
        </div>

        {/* ---------------- API KEY MANAGEMENT ---------------- */}
        <div className="bg-white p-5 rounded-xl shadow">
          <h2 className="text-sm font-semibold text-blue-900 mb-2">
            API Key Management
          </h2>

          <p className="text-xs text-gray-500 mb-4">
            Securely manage API keys for integrations.
          </p>

          <div className="flex gap-3">
            <input
              type="text"
              placeholder="Enter API Key..."
              className="border px-3 py-2 rounded-lg text-sm w-64"
            />

<button className="flex items-center gap-2 !bg-blue-600 !text-white px-4 py-2 rounded-lg shadow hover:!bg-blue-700">
              Save Key
            </button>
          </div>
        </div>

        {/* ---------------- API STATUS + LOGS ---------------- */}
        <div className="grid grid-cols-2 gap-6">

          {/* STATUS */}
          <div className="bg-white p-5 rounded-xl shadow">
            <h2 className="text-sm font-semibold text-blue-900 mb-2">
              Integration Status Monitoring
            </h2>

            <p className="text-xs text-gray-500 mb-4">
              Real-time status of connected APIs.
            </p>

            {integrations.slice(0, 5).map((int, i) => (
              <div key={i} className="flex justify-between mb-3 text-sm">
                <span>{int.name}</span>

                {int.status === "Connected" ? (
                  <span className="text-green-600 flex items-center gap-1">
                    <CheckCircle size={14} /> Active
                  </span>
                ) : (
                  <span className="text-gray-400 flex items-center gap-1">
                    <XCircle size={14} /> Inactive
                  </span>
                )}
              </div>
            ))}
          </div>

          {/* LOGS */}
          <div className="bg-white p-5 rounded-xl shadow">
            <h2 className="text-sm font-semibold text-blue-900 mb-2">
              API Call Logs
            </h2>

            <p className="text-xs text-gray-500 mb-4">
              Logs of recent API activity across integrations.
            </p>

            {apiLogs.map((log, i) => (
              <div key={i} className="flex justify-between mb-3 text-sm">
                <div>
                  <p className="text-gray-800">{log.api}</p>
                  <span className="text-xs text-gray-400">{log.action}</span>
                </div>

                <span
                  className={`text-xs ${
                    log.status === "Success"
                      ? "text-green-600"
                      : "text-red-600"
                  }`}
                >
                  {log.status}
                </span>
              </div>
            ))}
          </div>

        </div>

      </div>
    </div>
  );
}


// ---------------- CARD ----------------
const Card = ({ title, value, subtitle, desc, Icon, color }) => {
  const colors = {
    blue: "bg-blue-100 text-blue-600",
    green: "bg-green-100 text-green-600",
    purple: "bg-purple-100 text-purple-600",
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