// src/components/admin/UsersTable.jsx
import { ShieldCheck, Lock, Unlock } from "lucide-react";
import { Link } from "react-router-dom";
const UsersTable = ({ users, onToggleStatus }) => {
  return (
    <div className="bg-white rounded-xl shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">User Management</h2>
        <Link
          to="/admin/users"
          className="px-4 py-2 border-2 border-blue-600 text-blue-600 rounded-xl font-medium hover:bg-blue-600 hover:text-white transition-all duration-200"
        >
          View All Users
        </Link>
    
      </div>

      <table className="w-full text-left">
        <thead className="text-gray-500 text-sm border-b">
          <tr>
            <th className="py-3">User ID</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => {
            const isAdmin = user.role === "Admin";
            const isBlocked = user.status === "blocked";

            return (
              <tr key={user.user_id} className="border-b">
                <td className="py-4">{user.user_id}</td>
                <td>{user.email}</td>
                <td>{user.role}</td>
                <td>
                  <span
                    className={`px-3 py-1 rounded-full text-sm ${
                      isBlocked
                        ? "bg-red-100 text-red-600"
                        : "bg-green-100 text-green-600"
                    }`}
                  >
                    {user.status}
                  </span>
                </td>
                <td>
                  {isAdmin ? (
                    <button
                      disabled
                      className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-black rounded-lg"
                    >
                      <ShieldCheck size={16} />
                      Protected
                    </button>
                  ) : (
                    <button
                      onClick={() => onToggleStatus(user.user_id)}
                      className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-black rounded-lg hover:bg-gray-300"
                    >
                      {isBlocked ? <Unlock size={16} /> : <Lock size={16} />}
                      {isBlocked ? "Unblock" : "Block"}
                    </button>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default UsersTable;