// src/pages/AdminSecurity.jsx

import {
  AlertTriangle,
  Activity,
  Lock,
  ShieldCheck,
} from "lucide-react";

export default function AdminSecurity() {

  // -------- MOCK DATA --------
  const alerts = [
    { level: "High", msg: "Multiple failed login attempts", time: "2 min ago" },
    { level: "Medium", msg: "New device login detected", time: "10 min ago" },
    { level: "Low", msg: "Password updated", time: "1 hr ago" },
  ];

  const logs = [
    { user: "john@example.com", action: "Login", time: "10:30 AM" },
    { user: "alice@example.com", action: "Password Reset", time: "9:15 AM" },
    { user: "bob@example.com", action: "Logout", time: "8:45 AM" },
  ];

  const compliance = [
    { name: "GDPR", status: "Compliant" },
    { name: "HIPAA", status: "Compliant" },
    { name: "PCI-DSS", status: "Pending" },
  ];

  return (
    <div className="p-6 space-y-6 overflow-y-auto">

      {/* HEADER */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-blue-900">
          Security Panel
        </h1>
        <p className="text-gray-500 text-sm">
          Monitor threats, user access, encryption, and compliance status.
        </p>
      </div>

      {/* ---------------- KPI CARDS ---------------- */}
      <div className="grid grid-cols-4 gap-6">

        <Card
          title="Threat Alerts"
          value="12"
          subtitle="3 high severity"
          desc="Detected potential threats and security incidents"
          Icon={AlertTriangle}
          color="red"
        />

        <Card
          title="Active Sessions"
          value="84"
          subtitle="Stable activity"
          desc="Currently active user sessions across the system"
          Icon={Activity}
          color="blue"
        />

        <Card
          title="Encryption Status"
          value="Enabled"
          subtitle="AES-256"
          desc="All sensitive data is securely encrypted"
          Icon={Lock}
          color="green"
        />

        <Card
          title="Compliance"
          value="2 / 3"
          subtitle="1 pending"
          desc="Regulatory compliance across security standards"
          Icon={ShieldCheck}
          color="purple"
        />

      </div>

      {/* ---------------- ALERTS + LOGIN ---------------- */}
      <div className="grid grid-cols-2 gap-6">

        {/* ALERTS */}
        <div className="bg-white p-5 rounded-xl shadow">
          <h2 className="text-sm font-semibold text-blue-900 mb-2">
            Real-time Threat Alerts
          </h2>

          <p className="text-xs text-gray-500 mb-3">
            Live monitoring of suspicious activity and potential risks.
          </p>

          {alerts.map((a, i) => (
            <div key={i} className="flex justify-between mb-3 text-sm">
              <div>
                <p className="font-medium text-gray-800">{a.msg}</p>
                <span className="text-xs text-gray-400">{a.level}</span>
              </div>
              <span className="text-xs text-gray-400">{a.time}</span>
            </div>
          ))}

          <p className="text-xs text-gray-400 mt-2">
            Helps quickly identify and respond to security threats.
          </p>
        </div>

        {/* LOGIN DETECTION */}
        <div className="bg-white p-5 rounded-xl shadow">
          <h2 className="text-sm font-semibold text-blue-900 mb-2">
            Suspicious Login Detection
          </h2>

          <p className="text-xs text-gray-500 mb-3">
            Detects unusual login behavior across devices and locations.
          </p>

          <p className="text-green-600 text-sm">
            No suspicious activity detected
          </p>

          <p className="text-xs text-gray-400 mt-2">
            Ensures account safety and prevents unauthorized access.
          </p>
        </div>

      </div>

      {/* ---------------- LOGS + COMPLIANCE ---------------- */}
      <div className="grid grid-cols-2 gap-6">

        {/* ACCESS LOGS */}
        <div className="bg-white p-5 rounded-xl shadow">
          <h2 className="text-sm font-semibold text-blue-900 mb-2">
            User Access Logs
          </h2>

          <p className="text-xs text-gray-500 mb-3">
            Records all user actions for auditing and monitoring.
          </p>

          {logs.map((log, i) => (
            <div key={i} className="flex justify-between mb-3 text-sm">
              <div>
                <p className="text-gray-800">{log.user}</p>
                <span className="text-xs text-gray-400">{log.action}</span>
              </div>
              <span className="text-xs text-gray-400">{log.time}</span>
            </div>
          ))}

          <p className="text-xs text-gray-400 mt-2">
            Useful for tracking activity and investigating incidents.
          </p>
        </div>

        {/* COMPLIANCE */}
        <div className="bg-white p-5 rounded-xl shadow">
          <h2 className="text-sm font-semibold text-blue-900 mb-2">
            Compliance Tracking
          </h2>

          <p className="text-xs text-gray-500 mb-3">
            Monitors adherence to industry security standards.
          </p>

          {compliance.map((c, i) => (
            <div key={i} className="flex justify-between mb-3 text-sm">
              <span className="text-gray-800">{c.name}</span>

              <span
                className={`px-2 py-1 rounded-full text-xs ${
                  c.status === "Compliant"
                    ? "bg-green-100 text-green-600"
                    : "bg-yellow-100 text-yellow-600"
                }`}
              >
                {c.status}
              </span>
            </div>
          ))}

          <p className="text-xs text-gray-400 mt-2">
            Ensures compliance with GDPR, HIPAA, and PCI-DSS standards.
          </p>
        </div>

      </div>

    </div>
  );
}


// ---------------- CARD ----------------
const Card = ({ title, value, subtitle, desc, Icon, color }) => {
  const colors = {
    red: "bg-red-100 text-red-600",
    blue: "bg-blue-100 text-blue-600",
    green: "bg-green-100 text-green-600",
    purple: "bg-purple-100 text-purple-600",
  };

  return (
    <div className="bg-white p-5 rounded-xl shadow flex justify-between">

      {/* TEXT */}
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

      {/* ICON */}
      <div className={`w-12 h-12 flex items-center justify-center rounded-full ${colors[color]}`}>
        <Icon size={20} />
      </div>

    </div>
  );
};