// src/components/admin/SecurityAlerts.jsx
import { AlertTriangle } from "lucide-react";

const alerts = [
  { text: "Unusual login detected", time: "2m ago" },
  { text: "Failed login attempts", time: "15m ago" },
  { text: "New device login", time: "1h ago" },
];

const SecurityAlerts = () => {
  return (
    <div className="bg-white rounded-xl shadow p-6">
      <h2 className="text-lg font-semibold mb-3">Security Alerts</h2>
      <div className="space-y-3">
        {alerts.map((alert, index) => (
          <div key={index} className="flex items-center gap-3">
            <AlertTriangle size={16} className="text-red-500" />
            <div>
              <p className="text-sm font-medium">{alert.text}</p>
              <p className="text-xs text-gray-500">{alert.time}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SecurityAlerts;