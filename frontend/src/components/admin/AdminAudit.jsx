// src/components/admin/AuditLogsTable.jsx
const AuditLogsTable = ({ logs }) => {
    return (
      <div className="bg-white shadow rounded-xl p-6">
        <h2 className="text-xl font-semibold mb-4">Security & Audit Logs</h2>
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b bg-gray-50">
              <th className="p-3">User ID</th>
              <th className="p-3">Action</th>
              <th className="p-3">Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.log_id} className="border-b hover:bg-gray-50">
                <td className="p-3">{log.user_id}</td>
                <td className="p-3">{log.action}</td>
                <td className="p-3">
                  {new Date(log.timestamp).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };
  
  export default AuditLogsTable;