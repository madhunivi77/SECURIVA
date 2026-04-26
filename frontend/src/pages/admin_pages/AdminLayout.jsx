// src/pages/admin_pages/AdminLayout.jsx
import { Outlet } from "react-router-dom";
import AdminSidebar from "../../components/admin/AdminSidebar";

const AdminLayout = () => {
  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      <AdminSidebar />
      <div className="flex-1 overflow-y-auto">
        <Outlet />
      </div>
    </div>
  );
};

export default AdminLayout;