import { useState, useEffect, Fragment } from "react";

const EVENT_LABELS = {
  signin: { label: "Sign In", color: "bg-blue-100 text-blue-700" },
  logout: { label: "Logout", color: "bg-gray-100 text-gray-700" },
  chat: { label: "Chat", color: "bg-purple-100 text-purple-700" },
  tool_call: { label: "Tool Call", color: "bg-indigo-100 text-indigo-700" },
  voice_session: { label: "Voice", color: "bg-amber-100 text-amber-700" },
  sms: { label: "SMS", color: "bg-teal-100 text-teal-700" },
  salesforce_connect: { label: "Salesforce", color: "bg-cyan-100 text-cyan-700" },
  error: { label: "Error", color: "bg-red-100 text-red-700" },
};

function Logs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [eventFilter, setEventFilter] = useState("");
  const [search, setSearch] = useState("");
  const [expandedRow, setExpandedRow] = useState(null);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (statusFilter) params.set("status", statusFilter);
      if (eventFilter) params.set("event", eventFilter);
      if (search) params.set("search", search);

      const res = await fetch(
        `http://localhost:8000/api/logs?${params.toString()}`,
        { credentials: "include" }
      );
      if (res.ok) {
        const data = await res.json();
        setLogs(data.logs);
      }
    } catch (err) {
      console.error("Failed to fetch logs:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [statusFilter, eventFilter]);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchLogs();
  };

  const formatTimestamp = (ts) => {
    if (!ts) return "-";
    const d = new Date(ts.includes("Z") ? ts : ts + "Z");
    return d.toLocaleString();
  };

  const formatDuration = (ms) => {
    if (!ms) return "-";
    if (ms < 1000) return `${Math.round(ms)}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const getEventBadge = (event) => {
    const cfg = EVENT_LABELS[event] || {
      label: event,
      color: "bg-gray-100 text-gray-600",
    };
    return (
      <span
        className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${cfg.color}`}
      >
        {cfg.label}
      </span>
    );
  };

  const getDescription = (log) => {
    const d = log.details || {};
    switch (log.event) {
      case "signin":
        return `${d.method === "google_oauth" ? "Google" : "Local"} login${log.user_email ? ` — ${log.user_email}` : ""}`;
      case "logout":
        return log.user_email || "User logged out";
      case "chat":
        return d.user_message
          ? d.user_message.slice(0, 100) + (d.user_message.length > 100 ? "..." : "")
          : `${d.model || "unknown"} — ${d.tool_calls_count || 0} tool calls`;
      case "tool_call":
        return d.tool_name || "Unknown tool";
      case "voice_session":
        return "Voice session started";
      case "sms":
        return `SMS to ${d.phone || "unknown"}`;
      default:
        return log.error || JSON.stringify(d).slice(0, 80);
    }
  };

  return (
    <div className="max-w-full">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold">Activity Logs</h1>
        <button
          onClick={fetchLogs}
          className="px-4 py-2 text-sm bg-gray-200 hover:bg-gray-300 rounded"
        >
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-4 flex-wrap">
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            placeholder="Search logs..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="px-3 py-1.5 border border-gray-300 rounded text-sm w-56"
          />
          <button
            type="submit"
            className="px-3 py-1.5 bg-gray-800 text-white rounded text-sm hover:bg-gray-700"
          >
            Search
          </button>
        </form>
        <select
          value={eventFilter}
          onChange={(e) => setEventFilter(e.target.value)}
          className="px-3 py-1.5 border border-gray-300 rounded text-sm"
        >
          <option value="">All events</option>
          <option value="signin">Sign In</option>
          <option value="logout">Logout</option>
          <option value="chat">Chat</option>
          <option value="tool_call">Tool Call</option>
          <option value="voice_session">Voice</option>
          <option value="sms">SMS</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-1.5 border border-gray-300 rounded text-sm"
        >
          <option value="">All statuses</option>
          <option value="success">Success</option>
          <option value="error">Error</option>
        </select>
      </div>

      {/* Log Table */}
      {loading ? (
        <p className="text-gray-500">Loading logs...</p>
      ) : logs.length === 0 ? (
        <p className="text-gray-500">No logs found.</p>
      ) : (
        <div className="overflow-x-auto border border-gray-200 rounded">
          <table className="w-full text-sm text-left">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 font-medium">Timestamp</th>
                <th className="px-4 py-3 font-medium">Event</th>
                <th className="px-4 py-3 font-medium">Description</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">User</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log, i) => (
                <Fragment key={i}>
                  <tr
                    className={`border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${
                      expandedRow === i ? "bg-gray-50" : ""
                    }`}
                    onClick={() =>
                      setExpandedRow(expandedRow === i ? null : i)
                    }
                  >
                    <td className="px-4 py-2.5 text-gray-600 whitespace-nowrap">
                      {formatTimestamp(log.timestamp)}
                    </td>
                    <td className="px-4 py-2.5">{getEventBadge(log.event)}</td>
                    <td className="px-4 py-2.5 max-w-md truncate">
                      {getDescription(log)}
                    </td>
                    <td className="px-4 py-2.5">
                      <span
                        className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                          log.status === "success"
                            ? "bg-green-100 text-green-700"
                            : "bg-red-100 text-red-700"
                        }`}
                      >
                        {log.status}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-gray-500 text-xs">
                      {log.user_email || log.user_id?.slice(0, 8) || "-"}
                    </td>
                  </tr>
                  {expandedRow === i && (
                    <tr className="bg-gray-50">
                      <td colSpan={5} className="px-4 py-3">
                        <div className="grid grid-cols-2 gap-4 text-xs">
                          <div>
                            <p className="font-medium text-gray-500 mb-1">
                              Details
                            </p>
                            <pre className="bg-white p-3 rounded border border-gray-200 overflow-auto max-h-48 whitespace-pre-wrap">
                              {JSON.stringify(log.details, null, 2)}
                            </pre>
                          </div>
                          <div>
                            <p className="font-medium text-gray-500 mb-1">
                              {log.error ? "Error" : "Info"}
                            </p>
                            <pre
                              className={`p-3 rounded border overflow-auto max-h-48 whitespace-pre-wrap ${
                                log.error
                                  ? "bg-red-50 border-red-200 text-red-800"
                                  : "bg-white border-gray-200"
                              }`}
                            >
                              {log.error ||
                                (log.event === "tool_call"
                                  ? log.details?.result || "No result"
                                  : "No errors")}
                            </pre>
                          </div>
                          {log.metadata && (
                            <div className="col-span-2">
                              <p className="font-medium text-gray-500 mb-1">
                                Metadata
                              </p>
                              <pre className="bg-white p-3 rounded border border-gray-200 overflow-auto max-h-32 whitespace-pre-wrap">
                                {JSON.stringify(log.metadata, null, 2)}
                              </pre>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="text-xs text-gray-400 mt-3">
        Showing {logs.length} log entries
      </p>
    </div>
  );
}

export default Logs;
