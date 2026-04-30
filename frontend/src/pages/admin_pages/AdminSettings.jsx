// src/pages/AdminSettings.jsx

import { useState } from "react";
import AdminSidebar from "../../components/admin/AdminSidebar";
import {
  User,
  Mail,
  Phone,
  Shield,
  Bell,
  Database,
  UserPlus,
} from "lucide-react";

export default function AdminSettings() {

  const [activeTab, setActiveTab] = useState("General");

  return (
    <div className="flex h-screen bg-gray-100 font-sans">

    
      {/* CONTENT */}
      <div className="flex-1 p-6 space-y-6 overflow-y-auto">

        {/* HEADER */}
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-blue-900">
            Admin Profile & Settings
          </h1>
          <p className="text-gray-500 text-sm">
            Manage admin details, system settings, and access controls.
          </p>
        </div>

        {/* ---------------- ADMIN INFO ---------------- */}
        <div className="bg-white p-6 rounded-xl shadow">

          <h2 className="text-sm font-semibold text-blue-900 mb-4">
            Admin Information
          </h2>

          <div className="grid grid-cols-3 gap-6">

            <InfoCard icon={User} label="Name" value="Admin" />
            <InfoCard icon={Mail} label="Email" value="admin@example.com" />
            <InfoCard icon={Phone} label="Contact" value="+1 123 456 7890" />

          </div>
        </div>

        {/* ---------------- SETTINGS TABS ---------------- */}
        <div className="bg-white p-6 rounded-xl shadow">

          {/* Tabs */}
          <div className="flex gap-6 border-b pb-3 mb-4">

            {["General", "Notifications", "Database", "Security", "Add Admin"].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`text-sm font-medium ${
                  activeTab === tab
                    ? "text-blue-600 border-b-2 border-blue-600 pb-1"
                    : "text-gray-500"
                }`}
              >
                {tab}
              </button>
            ))}

          </div>

          {/* TAB CONTENT */}

          {activeTab === "General" && (
            <div className="space-y-4">
              <SettingItem title="Account Name" />
              <SettingItem title="Email Preferences" />
              <SettingItem title="Language & Region" />
            </div>
          )}

          {activeTab === "Notifications" && (
            <div className="space-y-4">
              <SettingItem title="Email Notifications" />
              <SettingItem title="Push Notifications" />
              <SettingItem title="Security Alerts" />
            </div>
          )}

          {activeTab === "Database" && (
            <div className="space-y-4">
              <SettingItem title="Backup Settings" />
              <SettingItem title="Data Retention Policy" />
              <SettingItem title="Storage Usage" />
            </div>
          )}

          {activeTab === "Security" && (
            <div className="space-y-4">
              <SettingItem title="Password Policy" />
              <SettingItem title="2FA Authentication" />
              <SettingItem title="Access Control" />
            </div>
          )}

          {activeTab === "Add Admin" && (
            <div className="space-y-4">

              <input
                type="text"
                placeholder="Admin Name"
                className="w-full border p-2 rounded-lg text-sm"
              />

              <input
                type="email"
                placeholder="Admin Email"
                className="w-full border p-2 rounded-lg text-sm"
              />

<button className="flex items-center gap-2 !bg-blue-600 !text-white px-4 py-2 rounded-lg shadow hover:!bg-blue-700">
                <UserPlus size={16} /> Add Admin
              </button>

            </div>
          )}

        </div>

      </div>
    </div>
  );
}


// ---------------- INFO CARD ----------------
const InfoCard = ({ icon: Icon, label, value }) => (
  <div className="flex items-center gap-3">
    <div className="w-10 h-10 flex items-center justify-center rounded-full bg-blue-100 text-blue-600">
      <Icon size={18} />
    </div>

    <div>
      <p className="text-xs text-gray-400">{label}</p>
      <p className="text-sm font-medium text-gray-800">{value}</p>
    </div>
  </div>
);


// ---------------- SETTING ITEM ----------------
const SettingItem = ({ title }) => (
  <div className="flex justify-between items-center border-b pb-2">
    <span className="text-sm text-gray-700">{title}</span>

    <button className="text-blue-600 text-sm">Edit</button>
  </div>
);