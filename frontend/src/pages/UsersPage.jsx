import { useState } from "react";
import { Search, ShieldCheck, Lock, Unlock } from "lucide-react";
import { Link } from "react-router-dom";
import AdminSidebar from "../components/admin/AdminSidebar";

const UsersPage = () => {
  const [users, setUsers] = useState([
    { user_id: "user_001", email: "admin@securiva.com", role: "Admin", status: "active" },
    { user_id: "user_002", email: "alice@example.com", role: "User", status: "active" },
    { user_id: "user_003", email: "bob@example.com", role: "User", status: "blocked" },
    { user_id: "user_004", email: "charlie@example.com", role: "User", status: "active" },
  ]);

  const [searchTerm, setSearchTerm] = useState("");

  const toggleUserStatus = (userId) => {
    setUsers((prevUsers) =>
      prevUsers.map((user) =>
        user.user_id === userId
          ? {
              ...user,
              status: user.status === "active" ? "blocked" : "active",
            }
          : user
      )
    );
  };

  const filteredUsers = users.filter(
    (user) =>
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.user_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      <AdminSidebar />
      <div className="flex-1 p-6 overflow-y-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold text-gray-800">
            User Management
          </h1>
          <p className="text-gray-500">
            Manage platform users and their access.
          </p>
        </div>

        {/* Search */}
        <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-lg shadow border border-gray-200 w-full md:w-80">
          <Search className="text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Search users..."
            className="outline-none text-sm w-full"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-2xl shadow border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full text-left">
            <thead className="bg-gray-50 text-gray-600 text-sm uppercase">
              <tr>
                <th className="px-6 py-4">User ID</th>
                <th className="px-6 py-4">Email</th>
                <th className="px-6 py-4">Role</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="text-gray-700">
              {filteredUsers.map((user) => (
                <tr key={user.user_id} className="border-t hover:bg-gray-50 transition">
                  <td className="px-6 py-4 font-medium">
                    <Link
                      to={`/admin/users/${user.user_id}`}
                      className="text-blue-600 hover:underline"
                    >
                      {user.user_id}
                    </Link>
                  </td>
                  <td className="px-6 py-4">{user.email}</td>
                  <td className="px-6 py-4">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        user.role === "Admin"
                          ? "bg-blue-100 text-blue-700"
                          : "bg-gray-100 text-gray-700"
                      }`}
                    >
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        user.status === "active"
                          ? "bg-green-100 text-green-700"
                          : "bg-red-100 text-red-600"
                      }`}
                    >
                      {user.status.charAt(0).toUpperCase() +
                        user.status.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    {user.role === "Admin" ? (
                      <span className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-100 text-gray-700 cursor-not-allowed">
                        <ShieldCheck size={16} />
                        Protected
                      </span>
                    ) : (
                      <button
                        onClick={() => toggleUserStatus(user.user_id)}
                        className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg transition ${
                          user.status === "active"
                            ? "bg-red-50 text-red-600 hover:bg-red-100"
                            : "bg-green-50 text-green-600 hover:bg-green-100"
                        }`}
                      >
                        {user.status === "active" ? (
                          <>
                            <Lock size={16} />
                            Block
                          </>
                        ) : (
                          <>
                            <Unlock size={16} />
                            Unblock
                          </>
                        )}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredUsers.length === 0 && (
          <div className="p-6 text-center text-gray-500">
            No users found.
          </div>
        )}
      </div>
    </div>
    </div>
  );
};

export default UsersPage;