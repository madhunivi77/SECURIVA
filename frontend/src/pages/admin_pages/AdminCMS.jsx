// src/pages/AdminContent.jsx

import AdminSidebar from "../../components/admin/AdminSidebar";
import {
  FileText,
  Edit,
  Upload,
  History,
  Globe,
  Save,
} from "lucide-react";

export default function AdminContent() {

  // -------- MOCK DATA --------
  const pages = [
    { name: "Home Page", status: "Published" },
    { name: "About Page", status: "Draft" },
    { name: "Features Page", status: "Published" },
    { name: "Pricing Page", status: "Published" },
  ];

  const logs = [
    { action: "Updated FAQ", time: "10 min ago" },
    { action: "Published Blog Post", time: "1 hr ago" },
    { action: "Edited Terms & Policy", time: "Yesterday" },
  ];

  return (
    <div className="flex h-screen bg-gray-100 font-sans">

      {/* Sidebar */}
      <AdminSidebar />

      {/* CONTENT */}
      <div className="flex-1 p-6 space-y-6 overflow-y-auto">

        {/* HEADER */}
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-blue-900">
            Content Management
          </h1>
          <p className="text-gray-500 text-sm">
            Manage website content, blogs, policies, and SEO settings.
          </p>
        </div>

        {/* ---------------- KPI CARDS ---------------- */}
        <div className="grid grid-cols-4 gap-6">

          <Card
            title="Total Pages"
            value="12"
            subtitle="Across website"
            desc="All editable website pages"
            Icon={Globe}
            color="blue"
          />

          <Card
            title="Drafts"
            value="3"
            subtitle="Pending publish"
            desc="Content not yet published"
            Icon={Edit}
            color="orange"
          />

          <Card
            title="Published"
            value="9"
            subtitle="Live content"
            desc="Currently visible to users"
            Icon={FileText}
            color="green"
          />

          <Card
            title="Media Files"
            value="45"
            subtitle="Images & docs"
            desc="Uploaded media content"
            Icon={Upload}
            color="purple"
          />

        </div>

        {/* ---------------- EDITOR + SEO ---------------- */}
        <div className="grid grid-cols-2 gap-6">

          {/* RICH TEXT EDITOR */}
          <div className="bg-white p-5 rounded-xl shadow">
            <h2 className="text-sm font-semibold text-blue-900 mb-2">
              Content Editor
            </h2>

            <p className="text-xs text-gray-500 mb-3">
              Create and edit content with rich text formatting.
            </p>

            <textarea
              placeholder="Write content here..."
              className="w-full h-40 border rounded-lg p-3 text-sm"
            />

            <div className="flex gap-3 mt-3">
            <button className="flex items-center gap-2 !bg-blue-600 !text-white px-4 py-2 rounded-lg shadow hover:!bg-blue-700">
                <Save size={16} /> Save Draft
              </button>

              <button className="flex items-center gap-2 !bg-blue-600 !text-white px-4 py-2 rounded-lg shadow hover:!bg-blue-700">
                Publish
              </button>
            </div>
          </div>

          {/* SEO SETTINGS */}
          <div className="bg-white p-5 rounded-xl shadow">
            <h2 className="text-sm font-semibold text-blue-900 mb-2">
              SEO Settings
            </h2>

            <p className="text-xs text-gray-500 mb-3">
              Optimize content for search engines.
            </p>

            <input
              type="text"
              placeholder="Meta Title"
              className="w-full border rounded-lg p-2 text-sm mb-2"
            />

            <textarea
              placeholder="Meta Description"
              className="w-full border rounded-lg p-2 text-sm"
            />
          </div>

        </div>

        {/* ---------------- MEDIA + PAGES ---------------- */}
        <div className="grid grid-cols-2 gap-6">

          {/* MEDIA UPLOAD */}
          <div className="bg-white p-5 rounded-xl shadow">
            <h2 className="text-sm font-semibold text-blue-900 mb-2">
              Media Upload
            </h2>

            <p className="text-xs text-gray-500 mb-3">
              Upload images, videos, and documents.
            </p>

            <input type="file" className="mb-3" />

            <button className="flex items-center gap-2 !bg-blue-600 !text-white px-4 py-2 rounded-lg shadow hover:!bg-blue-700">
              Upload
            </button>
          </div>

          {/* WEBSITE PAGES */}
          <div className="bg-white p-5 rounded-xl shadow">
            <h2 className="text-sm font-semibold text-blue-900 mb-2">
              Website Pages
            </h2>

            <p className="text-xs text-gray-500 mb-3">
              Manage editable website sections.
            </p>

            {pages.map((p, i) => (
              <div key={i} className="flex justify-between mb-3 text-sm">
                <span>{p.name}</span>

                <span
                  className={`text-xs px-2 py-1 rounded-full ${
                    p.status === "Published"
                      ? "bg-green-100 text-green-600"
                      : "bg-gray-200 text-gray-500"
                  }`}
                >
                  {p.status}
                </span>
              </div>
            ))}
          </div>

        </div>

        {/* ---------------- VERSION HISTORY ---------------- */}
        <div className="bg-white p-5 rounded-xl shadow">
          <h2 className="text-sm font-semibold text-blue-900 mb-2">
            Version History & Activity
          </h2>

          <p className="text-xs text-gray-500 mb-3">
            Track changes and rollback previous versions.
          </p>

          {logs.map((log, i) => (
            <div key={i} className="flex justify-between mb-3 text-sm">
              <div className="flex items-center gap-2">
                <History size={14} />
                <span>{log.action}</span>
              </div>

              <span className="text-xs text-gray-400">{log.time}</span>
            </div>
          ))}
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