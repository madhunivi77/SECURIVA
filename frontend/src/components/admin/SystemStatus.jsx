// src/components/admin/SystemStatus.jsx
import { CheckCircle } from "lucide-react";

const SystemStatus = () => {
  return (
    <div className="bg-white rounded-xl shadow p-6">
      <h2 className="text-lg font-semibold mb-3">System Status</h2>
      <div className="flex items-center gap-2 text-green-600 mb-4">
        <CheckCircle size={18} />
        <span className="font-medium">All Systems Operational</span>
      </div>
      <p className="text-gray-500 text-sm">
        All core services are running smoothly.
      </p>
    </div>
  );
};

export default SystemStatus;