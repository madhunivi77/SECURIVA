import { useState } from "react";
import {
  ArrowLeft,
  Trash2,
  User,
  CreditCard,
  Shield,
  Crown,
  Activity,
  KeyRound,
  XCircle,
  CheckCircle,
  Mail,
  Phone,
  MapPin,
} from "lucide-react";
import { Link } from "react-router-dom";

const UserProfile = () => {
  const [activeTab, setActiveTab] = useState("profile");

  const user = {
    id: "user_001",
    name: "John Smith",
    email: "admin@securiva.com",
    phone: "+1 (555) 123-4567",
    address: "123 Main Street, New York, NY 10001",
    city: "New York, NY 10001",
    status: "Active",
    memberSince: "Dec 20, 2024",
    plan: "Premium",
    nextBilling: "Jan 20, 2025",
    lastLogin: "Dec 22, 2024, 10:30 AM",
    emailVerified: true,
    twoFactorAuth: true,
  };

  const tabs = [
    { id: "profile", label: "Profile", icon: User },
    { id: "payment", label: "Payment", icon: CreditCard },
    { id: "security", label: "Security", icon: Shield },
    { id: "plan", label: "Plan", icon: Crown },
    { id: "activity", label: "Activity", icon: Activity },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Breadcrumb */}
      <div className="text-sm text-gray-500">
        <span className="text-blue-600 font-medium">Users</span> / {user.id}
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold text-gray-800">
            User Profile
          </h1>
          <p className="text-gray-500">
            View and manage user account details and settings.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/admin/users"
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50"
          >
            <ArrowLeft size={16} />
            Back to Users
          </Link>

          <button className="flex items-center gap-2 px-4 py-2 bg-red-50 text-red-600 border border-red-200 rounded-lg hover:bg-red-100">
            <Trash2 size={16} />
            Delete User Account
          </button>
        </div>
      </div>

      {/* User Summary Card */}
      <div className="bg-white rounded-2xl shadow border border-gray-200 p-6 flex flex-col md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-4">
          <div className="w-20 h-20 rounded-full bg-blue-100 flex items-center justify-center">
            <User className="text-blue-600" size={40} />
          </div>

          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-xl font-semibold text-gray-800">
                {user.name}
              </h2>
              <span className="px-3 py-1 text-xs font-semibold bg-green-100 text-green-700 rounded-full">
                {user.status}
              </span>
            </div>
            <p className="text-gray-500">{user.email}</p>
            <p className="text-gray-500 flex items-center gap-2">
              <Phone size={14} /> {user.phone}
            </p>
            <p className="text-gray-500 flex items-center gap-2">
              <MapPin size={14} /> {user.address}
            </p>
            <p className="text-sm text-gray-400 mt-1">
              User ID: {user.id} • Member since {user.memberSince}
            </p>
          </div>
        </div>

        <div className="mt-4 md:mt-0 text-right">
          <span className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-full">
            Plan {user.plan}
          </span>
          <p className="text-gray-500 mt-2">
            Next billing: {user.nextBilling}
          </p>
          <button className="mt-3 px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200">
            Make Admin
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-6 border-b border-gray-200">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 pb-3 text-sm font-medium transition ${
                activeTab === tab.id
                  ? "text-blue-600 border-b-2 border-blue-600"
                  : "text-gray-500 hover:text-blue-600"
              }`}
            >
              <Icon size={16} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Personal Information */}
        <div className="bg-white rounded-2xl shadow border border-gray-200 p-6">
          <h3 className="text-lg font-semibold mb-4">Personal Information</h3>
          <div className="space-y-4 text-sm text-gray-600">
            <div>
              <label className="font-medium text-gray-500">Name</label>
              <p>{user.name}</p>
            </div>
            <div>
              <label className="font-medium text-gray-500">Email</label>
              <p>{user.email}</p>
            </div>
            <div>
              <label className="font-medium text-gray-500">Contact Number</label>
              <p>{user.phone}</p>
            </div>
            <div>
              <label className="font-medium text-gray-500">Address</label>
              <p>{user.address}</p>
            </div>
            <button className="mt-4 px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200">
              Edit Profile
            </button>
          </div>
        </div>

        {/* Payment Methods */}
        <div className="bg-white rounded-2xl shadow border border-gray-200 p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">Payment Methods</h3>
            <button className="px-3 py-1 text-sm bg-gray-100 rounded-lg hover:bg-gray-200">
              + Add Method
            </button>
          </div>

          <div className="space-y-3">
            <div className="border rounded-lg p-4 flex justify-between">
              <div>
                <p className="font-medium">Visa ending in 4242</p>
                <p className="text-sm text-gray-500">Expires 12/26</p>
              </div>
              <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                Default
              </span>
            </div>

            <div className="border rounded-lg p-4">
              <p className="font-medium">Mastercard ending in 8888</p>
              <p className="text-sm text-gray-500">Expires 08/25</p>
            </div>
          </div>
        </div>

        {/* Quick Actions & Status */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <div className="bg-white rounded-2xl shadow border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button className="w-full flex items-center gap-3 p-3 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100">
                <KeyRound size={18} />
                Reset Password
              </button>
              <button className="w-full flex items-center gap-3 p-3 bg-yellow-50 text-yellow-600 rounded-lg hover:bg-yellow-100">
                <XCircle size={18} />
                Cancel Plan
              </button>
              <button className="w-full flex items-center gap-3 p-3 bg-red-50 text-red-600 rounded-lg hover:bg-red-100">
                <Trash2 size={18} />
                Delete Account
              </button>
            </div>
          </div>

          {/* Account Status */}
          <div className="bg-white rounded-2xl shadow border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">Account Status</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span>Account Status</span>
                <span className="text-green-600 font-medium flex items-center gap-1">
                  <CheckCircle size={16} /> Active
                </span>
              </div>
              <div className="flex justify-between">
                <span>Email Verified</span>
                <span className="text-green-600 font-medium flex items-center gap-1">
                  <CheckCircle size={16} /> Yes
                </span>
              </div>
              <div className="flex justify-between">
                <span>Two-Factor Auth</span>
                <span className="text-green-600 font-medium flex items-center gap-1">
                  <CheckCircle size={16} /> Enabled
                </span>
              </div>
              <div className="flex justify-between">
                <span>Last Login</span>
                <span className="text-gray-600">{user.lastLogin}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;