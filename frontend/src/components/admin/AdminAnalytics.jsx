
import { Users, MessageSquare, Key, Shield } from "lucide-react";

const StatCard = ({ title, value, icon: Icon }) => (
  <div className="bg-white shadow rounded-xl p-5 flex items-center gap-4">
    <div className="p-3 bg-blue-100 rounded-full">
      <Icon className="text-blue-600" size={20} />
    </div>
    <div>
      <p className="text-gray-500 text-sm">{title}</p>
      <h3 className="text-2xl font-bold">{value}</h3>
    </div>
  </div>
);

const AnalyticsCards = ({ stats }) => {
  return (
    <div id="analytics-section" className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
      <StatCard title="Total Users" value={stats.total_users} icon={Users} />
      <StatCard title="Total Chats" value={stats.total_chats} icon={MessageSquare} />
      <StatCard title="Active Tokens" value={stats.total_tokens} icon={Key} />
      <StatCard title="Audit Logs" value={stats.total_logs} icon={Shield} />
    </div>
  );
};

export default AnalyticsCards;