import { useState } from "react";
import { Calendar, Download } from "lucide-react";

import {
  LineChart,
  Line,
  XAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import {
    DollarSign,
    BarChart3,
    Key,
    ShieldAlert
  } from "lucide-react";

export default function AdminPayments() {
  // ---------------- STATE ----------------
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [planFilter, setPlanFilter] = useState("All");

  // ---------------- MOCK DATA ----------------
  const payments = [
    {
      id: "TXN-001256",
      user: "John Smith",
      email: "john@example.com",
      plan: "Premium Plan",
      amount: "$29.99",
      status: "Paid",
      method: "Visa •••• 4242",
      date: "Dec 23, 2024",
    },
    {
      id: "TXN-001251",
      user: "Lisa Martinez",
      email: "lisa@example.com",
      plan: "Premium Plan",
      amount: "$29.99",
      status: "Failed",
      method: "Mastercard •••• 8888",
      date: "Dec 21, 2024",
    },
    {
      id: "TXN-001250",
      user: "James Taylor",
      email: "james@example.com",
      plan: "Base Plan",
      amount: "$9.99",
      status: "Paid",
      method: "Visa •••• 9012",
      date: "Dec 20, 2024",
    },
  ];

  // ---------------- FILTER LOGIC ----------------
  const filteredPayments = payments.filter((p) => {
    const matchesSearch =
      p.user.toLowerCase().includes(search.toLowerCase()) ||
      p.email.toLowerCase().includes(search.toLowerCase());

    const matchesStatus =
      statusFilter === "All" || p.status === statusFilter;

    const matchesPlan =
      planFilter === "All" || p.plan === planFilter;

    return matchesSearch && matchesStatus && matchesPlan;
  });
  
  const Card = ({ title, value, change, changeColor, Icon, color }) => {
    const colors = {
      blue: "bg-blue-100 text-blue-600",
      green: "bg-green-100 text-green-600",
      purple: "bg-purple-100 text-purple-600",
      orange: "bg-orange-100 text-orange-600",
    };
  
    return (
      <div className="bg-white p-5 rounded-xl shadow flex items-center justify-between">
  
        {/* LEFT TEXT */}
        <div>
          <p className="text-gray-500 text-sm mb-1">{title}</p>
          <h2 className="text-2xl font-bold text-blue-900">{value}</h2>
  
          {/* CHANGE TEXT */}
          <p className={`text-sm mt-1 ${changeColor}`}>
            {change} <span className="text-gray-400">vs last 30 days</span>
          </p>
        </div>
  
        {/* ICON CIRCLE */}
        <div className={`w-12 h-12 rounded-full flex items-center justify-center ${colors[color]}`}>
          <Icon size={20} />
        </div>
  
      </div>
    );
  };
  
  // ---------------- CHART DATA ----------------
  const revenueData = [
    { name: "Nov 23", value: 5000 },
    { name: "Nov 30", value: 12000 },
    { name: "Dec 7", value: 18000 },
    { name: "Dec 14", value: 22000 },
    { name: "Dec 23", value: 30000 },
  ];

  const planData = [
    { name: "Premium", value: 62 },
    { name: "Base", value: 45 },
    { name: "Add-on", value: 21 },
  ];

  const COLORS = ["#3b82f6", "#10b981", "#f59e0b"];

  const refunds = [
    { name: "Sarah Johnson", amount: "-$29.99", date: "Dec 18, 2024" },
    { name: "Michael Brown", amount: "-$9.99", date: "Dec 15, 2024" },
    { name: "Emily Davis", amount: "-$19.99", date: "Dec 12, 2024" },
  ];

  return (
    <div className="p-6 space-y-6 overflow-y-auto">

      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-blue-900">Payments</h1>
          <p className="text-gray-500">
            View and manage all subscription payments and transactions.
          </p>
        </div>

        <div className="flex gap-3">
          <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-lg shadow">
            <Calendar size={16} />
            Nov 23 - Dec 23
          </div>

          <button className="flex items-center gap-2 !bg-blue-600 !text-white px-4 py-2 rounded-lg shadow hover:!bg-blue-700">
            <Download size={16} />
            Export Report
          </button>
        </div>
      </div>

      {/* Cards */}
      <div className="grid grid-cols-4 gap-6">
        <Card
          title="Total Revenue"
          value="$24,580.50"
          change="+18.6%"
          changeColor="text-green-600"
          Icon={DollarSign}
          color="blue"
        />

        <Card
          title="Total Transactions"
          value="256"
          change="+12.4%"
          changeColor="text-green-600"
          Icon={BarChart3}
          color="green"
        />

        <Card
          title="Active Subscriptions"
          value="128"
          change="+8.7%"
          changeColor="text-green-600"
          Icon={Key}
          color="purple"
        />

        <Card
          title="Refunds"
          value="$1,230.00"
          change="-4.2%"
          changeColor="text-red-500"
          Icon={ShieldAlert}
          color="orange"
        />
      </div>

      {/* Transactions */}
      <div className="bg-white rounded-xl shadow p-6">

        {/* Filters */}
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Transactions</h2>

          <div className="flex gap-3">

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 border rounded-lg text-sm"
            >
              <option value="All">All Status</option>
              <option value="Paid">Paid</option>
              <option value="Failed">Failed</option>
            </select>

            <select
              value={planFilter}
              onChange={(e) => setPlanFilter(e.target.value)}
              className="px-3 py-2 border rounded-lg text-sm"
            >
              <option value="All">All Plans</option>
              <option value="Premium Plan">Premium Plan</option>
              <option value="Base Plan">Base Plan</option>
            </select>

            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search user or email..."
              className="px-3 py-2 border rounded-lg text-sm"
            />
          </div>
        </div>

        {/* Table */}
        <table className="w-full text-left">
          <thead className="text-gray-500 text-sm border-b">
            <tr>
              <th className="py-3">Transaction ID</th>
              <th>User</th>
              <th>Plan</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Method</th>
              <th>Date</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>
            {filteredPayments.length > 0 ? (
              filteredPayments.map((p) => (
                <tr key={p.id} className="border-b">
                  <td className="py-4 text-blue-600">{p.id}</td>

                  <td>
                    <div>{p.user}</div>
                    <div className="text-sm text-gray-400">{p.email}</div>
                  </td>

                  <td>{p.plan}</td>
                  <td>{p.amount}</td>

                  <td>
                    <span
                      className={`px-3 py-1 rounded-full text-sm ${
                        p.status === "Paid"
                          ? "bg-green-100 text-green-600"
                          : "bg-red-100 text-red-600"
                      }`}
                    >
                      {p.status}
                    </span>
                  </td>

                  <td>{p.method}</td>
                  <td>{p.date}</td>

                  <td className="text-blue-600 cursor-pointer">
                    {p.status === "Failed" ? "Retry" : "View"}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="8" className="text-center py-6 text-gray-400">
                  No transactions found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-3 gap-6">

        {/* Revenue Chart */}
        <div className="bg-white p-5 rounded-xl shadow">
          <h3 className="font-semibold mb-2">Revenue Overview</h3>
          <p className="text-xl font-semibold">$24,580.50</p>
          <p className="text-green-600 text-sm mb-2">+18.6%</p>

          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={revenueData}>
              <XAxis dataKey="name" />
              <Tooltip />
              <Line dataKey="value" stroke="#2563eb" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Pie */}
        <div className="bg-white p-5 rounded-xl shadow">
          <h3 className="font-semibold mb-4 text-blue-900">
            Subscription by Plan
          </h3>

          <div className="flex items-center gap-6">

            {/* DONUT CHART */}
            <PieChart width={180} height={180}>
              <Pie
                data={planData}
                dataKey="value"
                innerRadius={50}
                outerRadius={70}
                paddingAngle={2}
              >
                {planData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i]} />
                ))}
              </Pie>
            </PieChart>

            {/* LEGEND (RIGHT SIDE) */}
            <div className="space-y-3 text-sm">

              {planData.map((p, i) => {
                const total = planData.reduce((sum, x) => sum + x.value, 0);
                const percent = ((p.value / total) * 100).toFixed(1);

                return (
                  <div key={i} className="flex items-center gap-3">

                    {/* COLOR DOT */}
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: COLORS[i] }}
                    />

                    {/* LABEL */}
                    <span className="text-gray-700 w-24">
                      {p.name}
                    </span>

                    {/* VALUE */}
                    <span className="text-gray-500">
                      {p.value} ({percent}%)
                    </span>

                  </div>
                );
              })}

            </div>

          </div>
        </div>

        {/* Refunds */}
        <div className="bg-white p-5 rounded-xl shadow">
          <h3 className="font-semibold mb-4">Recent Refunds</h3>

          {refunds.map((r, i) => (
            <div key={i} className="flex justify-between text-sm mb-2">
              <span>{r.name}</span>
              <span className="text-red-500">{r.amount}</span>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}

