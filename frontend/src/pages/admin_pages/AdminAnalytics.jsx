// src/pages/AdminAnalytics.jsx

import AdminSidebar from "../../components/admin/AdminSidebar";
import {
  Users,
  UserPlus,
  DollarSign,
  Activity,
  Bot,
  Workflow,
  ShieldAlert,
} from "lucide-react";

import {
  LineChart,
  Line,
  XAxis,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";

export default function AdminAnalytics() {

  // -------- DATA --------
  const userGrowth = [
    { name: "Mon", users: 120 },
    { name: "Tue", users: 200 },
    { name: "Wed", users: 300 },
    { name: "Thu", users: 250 },
    { name: "Fri", users: 400 },
  ];

  const revenueData = [
    { name: "Jan", revenue: 12000 },
    { name: "Feb", revenue: 18000 },
    { name: "Mar", revenue: 24000 },
    { name: "Apr", revenue: 30000 },
  ];

  return (
    <div className="flex h-screen bg-gray-100 font-sans">

      {/* Sidebar */}
      <AdminSidebar />

      {/* Content */}
      <div className="flex-1 p-6 space-y-6 overflow-y-auto">

        {/* HEADER */}
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-blue-900">
            Analytics Dashboard
          </h1>
          <p className="text-gray-500 text-sm">
            Monitor user activity, revenue growth, and system performance.
          </p>
        </div>

        {/* ---------------- KPI CARDS ---------------- */}
        <div className="grid grid-cols-4 gap-6">

          <Card
            title="Active Users"
            value="1,245"
            subtitle="+12% growth this week"
            desc="Number of users currently active on the platform"
            Icon={Users}
            color="blue"
          />

          <Card
            title="New Registrations"
            value="320"
            subtitle="+8% vs last week"
            desc="New users who signed up recently"
            Icon={UserPlus}
            color="green"
          />

          <Card
            title="Revenue (Monthly)"
            value="$24,580"
            subtitle="+18.6% growth"
            desc="Total revenue generated this month"
            Icon={DollarSign}
            color="purple"
          />

          <Card
            title="API Usage"
            value="12K calls"
            subtitle="Stable usage"
            desc="Total API requests made by users"
            Icon={Activity}
            color="orange"
          />

        </div>

        {/* SECOND ROW */}
        <div className="grid grid-cols-3 gap-6">

          <Card
            title="AI Interactions"
            value="8,540"
            subtitle="Voice + Text"
            desc="Total AI conversations across platform"
            Icon={Bot}
            color="blue"
          />

          <Card
            title="Workflow Usage"
            value="1,240 runs"
            subtitle="+5% increase"
            desc="Automation workflows executed by users"
            Icon={Workflow}
            color="green"
          />

          <Card
            title="Security Alerts"
            value="12"
            subtitle="3 high priority"
            desc="Detected security incidents and threats"
            Icon={ShieldAlert}
            color="red"
          />

        </div>

        {/* ---------------- CHARTS ---------------- */}
        <div className="grid grid-cols-2 gap-6">

          {/* USER BEHAVIOR */}
          <div className="bg-white p-5 rounded-xl shadow">
            <h2 className="text-sm font-semibold text-blue-900 mb-2">
              User Behavior Tracking
            </h2>

            <p className="text-xs text-gray-500 mb-3">
              Tracks how users engage with the platform daily.
            </p>

            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={userGrowth}>
                <XAxis dataKey="name" />
                <Tooltip />
                <Line dataKey="users" stroke="#2563eb" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>

            <p className="text-xs text-gray-400 mt-2">
              Helps identify peak engagement times and trends.
            </p>
          </div>

          {/* REVENUE */}
          <div className="bg-white p-5 rounded-xl shadow">
            <h2 className="text-sm font-semibold text-blue-900 mb-2">
              Revenue Analytics
            </h2>

            <p className="text-xs text-gray-500 mb-3">
              Monthly revenue growth and financial performance.
            </p>

            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={revenueData}>
                <XAxis dataKey="name" />
                <Tooltip />
                <Bar dataKey="revenue" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>

            <p className="text-xs text-gray-400 mt-2">
              Used to track growth and optimize pricing strategy.
            </p>
          </div>

        </div>

        {/* ---------------- INSIGHTS ---------------- */}
        <div className="grid grid-cols-2 gap-6">

          <div className="bg-white p-5 rounded-xl shadow">
            <h2 className="text-sm font-semibold text-blue-900">
              Conversion Rate
            </h2>

            <p className="text-3xl font-bold text-blue-900 mt-2">32%</p>

            <p className="text-green-600 text-sm">
              +5.2% vs last month
            </p>

            <p className="text-xs text-gray-400 mt-2">
              Percentage of users upgrading to premium plans.
            </p>
          </div>

          <div className="bg-white p-5 rounded-xl shadow">
            <h2 className="text-sm font-semibold text-blue-900">
              System Performance
            </h2>

            <p className="text-3xl font-bold text-blue-900 mt-2">98.9%</p>

            <p className="text-gray-500 text-sm">Uptime</p>

            <p className="text-xs text-gray-400 mt-2">
              Measures platform reliability and stability.
            </p>
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
    orange: "bg-orange-100 text-orange-600",
    red: "bg-red-100 text-red-600",
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