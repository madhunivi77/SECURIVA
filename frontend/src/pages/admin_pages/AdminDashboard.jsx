// src/pages/AdminDashboard.jsx
import { useState } from "react";
import AdminSidebar from "../../components/admin/AdminSidebar";
import AnalyticsCards from "../../components/admin/AnalyticsCards";
import UsersTable from "../../components/admin/AdminUsertable";
import SystemStatus from "../../components/admin/SystemStatus";
import SecurityAlerts from "../../components/admin/SecurityAlerts";
import { Calendar, Download } from "lucide-react";

const AdminDashboard = () => {
  const [users, setUsers] = useState([
    { user_id: "user_001", email: "admin@securiva.com", role: "Admin", status: "active" },
    { user_id: "user_002", email: "abc@example.com", role: "User", status: "active" },
    { user_id: "user_003", email: "123@example.com", role: "User", status: "blocked" },
    { user_id: "user_004", email: "789@example.com", role: "User", status: "active" },
  ]);

  const toggleUserStatus = (userId) => {
    setUsers((prev) =>
      prev.map((user) =>
        user.user_id === userId
          ? {
              ...user,
              status: user.status === "active" ? "blocked" : "active",
            }
          : user
      )
    );
  };

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      <AdminSidebar />

      <div className="flex-1 p-6 overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
          <h1 className="text-2xl font-semibold tracking-tight text-blue-900">Welcome John </h1>
         
            <p className="text-gray-500">
              Admin Dashboard
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-lg shadow">
              <Calendar size={16} />
              <span className="text-sm">Nov 23, 2024 - Dec 23, 2024</span>
            </div>
            <button className="flex items-center gap-2 !bg-blue-600 !text-white px-4 py-2 rounded-lg shadow hover:!bg-blue-700">
                <Download size={16} />
                Export Report
                </button>
          </div>
        </div>

        {/* Analytics Cards */}
        <AnalyticsCards />

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
          <div className="lg:col-span-2">
            <UsersTable users={users} onToggleStatus={toggleUserStatus} />
          </div>
          <div className="space-y-6">
            <SystemStatus />
            <SecurityAlerts />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;