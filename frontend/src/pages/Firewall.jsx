import { Fragment, useEffect, useState } from "react";

const severityStyles = {
    critical: "bg-red-700 text-red-50",
    high: "bg-amber-700 text-amber-50",
    medium: "bg-yellow-500 text-yellow-50",
    low: "bg-green-700 text-green-50",
};

const severityDot = {
    critical: "bg-red-600",
    high: "bg-red-500",
    medium: "bg-amber-500",
    low: "bg-green-500",
};

function getSeverityBadge(severity) {
    return (
        <span className={`text-xs font-medium px-2 py-1 rounded-md uppercase tracking-wide ${severityStyles[severity]}`}>
            {severity}
        </span>
    )
}

const formatTimestamp = (ts) => {
    const date = new Date(ts);
    return date.toUTCString().replace("GMT", "UTC");
};

function Alerts() {
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isOpen, setIsOpen] = useState(false);
    const [selectedRow, setSelectedRow] = useState(null);

    useEffect(() => {
        fetchAlerts();
    }, []);

    const handleRowClick = (row) => {
        setSelectedRow(row);
        setIsOpen(true);
    };

    const fetchAlerts = async () => {
        setLoading(true);
        try {

            const res = await fetch(
                `http://localhost:8000/security/firewall`,
                { credentials: "include" }
            );
            if (res.ok) {
                const data = await res.json();
                setAlerts(data.response.alerts);
            }
        } catch (err) {
            console.error("Failed to fetch alerts:", err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-full">
            <div className="flex items-center justify-between mb-6">
                <h1 className="text-2xl font-semibold">Alert Logs</h1>
                <button
                    onClick={fetchAlerts}
                    className="px-4 py-2 text-sm hover:bg-white rounded"
                    style={{ background: "var(--bg-elev)", border: "1px solid var(--ivory-3)" }}
                >
                    Refresh
                </button>
            </div>

            {/* Log Table */}
            {loading ? (
                <p className="text-gray-500">Loading alerts...</p>
            ) : alerts.length === 0 ? (
                <p className="text-gray-500">No alerts found.</p>
            ) : (
                <div className="overflow-x-auto border rounded" style={{ borderColor: "var(--ink-soft)" }}>
                    <table className="w-full text-sm text-left">
                        <thead className="border-b" style={{ background: "var(--bg-elev)", border: "1px solid var(--ivory-3)" }}>
                            <tr>
                                <th className="px-4 py-3 font-medium">Timestamp</th>
                                <th className="px-4 py-3 font-medium">Summary</th>
                                <th className="px-4 py-3 font-medium">Source IP</th>
                                <th className="px-4 py-3 font-medium">Destination IP</th>
                                <th className="px-4 py-3 font-medium">Port</th>
                                <th className="px-4 py-3 font-medium">Severity</th>
                            </tr>
                        </thead>
                        <tbody>
                            {alerts.map((alert, i) => (
                                <Fragment key={i}>
                                    <tr
                                        className={`border-b border-gray-100 cursor-pointer hover:bg-blue-950`}
                                        style={{ border: "1px solid var(--ivory-3)" }}
                                        onClick={() => { handleRowClick(alert) }// trigger modal
                                        }
                                    >
                                        <td className="px-4 py-2.5 text-gray-600 whitespace-nowrap">
                                            {formatTimestamp(alert.timestamp)}
                                        </td>
                                        <td className="px-4 py-2.5 max-w-md truncate">
                                            {alert.summary}
                                        </td>
                                        <td className="px-4 py-2.5">
                                            {alert.src_ip}
                                        </td>
                                        <td className="px-4 py-2.5">
                                            {alert.dest_ip}
                                        </td>
                                        <td className="px-4 py-2.5">
                                            {alert.dest_port}
                                        </td>
                                        <td className="px-4 py-2.5 text-gray-500 text-xs">
                                            {getSeverityBadge(alert.severity)}
                                        </td>
                                    </tr>
                                </Fragment>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {isOpen && <SecurityEventModal event={selectedRow} onClose={() => { setIsOpen(false) }} />}

            <p className="text-xs text-gray-400 mt-3">
                Showing {alerts.length} alert entries
            </p>
        </div>
    );
}

const SecurityEventModal = ({ event, onClose }) => {

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
            <div className="bg-zinc-900 border border-zinc-700 rounded-xl w-full max-w-lg max-h-[85vh] overflow-y-auto flex flex-col">

                {/* Header */}
                <div className="sticky top-0 bg-zinc-900 border-b border-zinc-700 px-5 py-4 flex items-start justify-between gap-3 z-10">
                    <div className="flex items-start gap-3">
                        <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${severityDot[event.severity]}`} />
                        <div className="flex flex-col gap-0.5">
                            <p className="text-sm font-medium text-zinc-100 leading-snug">{event.summary}</p>
                            <p className="text-xs text-zinc-400">
                                {formatTimestamp(event.timestamp)} · {event.event_id}
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                        {getSeverityBadge(event.severity)}
                        <button
                            onClick={onClose}
                            className="text-zinc-400 hover:text-zinc-200 text-lg leading-none"
                        >
                            ✕
                        </button>
                    </div>
                </div>

                {/* Body */}
                <div className="px-5 py-4 flex flex-col gap-4">

                    {/* Source / Destination */}
                    <div className="flex gap-2">
                        <div className="flex-1 bg-zinc-800 rounded-lg px-3 py-2.5 flex flex-col gap-0.5">
                            <p className="text-xs text-zinc-400 uppercase tracking-wide">Source</p>
                            <p className="text-sm font-medium text-zinc-100 font-mono">{event.src_ip}</p>
                            <p className="text-xs text-zinc-400">port {event.src_port}</p>
                        </div>
                        <div className="flex-1 bg-zinc-800 rounded-lg px-3 py-2.5 flex flex-col gap-0.5">
                            <p className="text-xs text-zinc-400 uppercase tracking-wide">Destination</p>
                            <p className="text-sm font-medium text-zinc-100 font-mono">{event.dest_ip}</p>
                            <p className="text-xs text-zinc-400">port {event.dest_port}</p>
                        </div>
                    </div>

                    {/* Protocol / Sensor / Type */}
                    <div className="flex gap-2">
                        {[
                            { label: "Protocol", value: event.proto },
                            { label: "Sensor", value: event.sensor_id },
                            { label: "Type", value: event.event_type },
                        ].map(({ label, value }) => (
                            <div key={label} className="flex-1 bg-zinc-800 rounded-lg px-3 py-2.5 flex flex-col gap-0.5">
                                <p className="text-xs text-zinc-400 uppercase tracking-wide">{label}</p>
                                <p className="text-sm font-medium text-zinc-100">{value}</p>
                            </div>
                        ))}
                    </div>

                    {/* Category */}
                    <div className="border border-zinc-700 rounded-lg px-3 py-2.5 flex flex-col gap-1">
                        <p className="text-xs text-zinc-400 uppercase tracking-wide">Category</p>
                        <p className="text-sm text-zinc-100">{event.category}</p>
                    </div>

                    {/* Raw Signature */}
                    <div className="border border-zinc-700 rounded-lg px-3 py-2.5 flex flex-col gap-2">
                        <p className="text-xs text-zinc-400 uppercase tracking-wide">Raw signature</p>
                        <div className="flex flex-col gap-1">
                            {Object.entries(event.raw).map(([key, value]) => (
                                <div key={key} className="flex items-center justify-between">
                                    <span className="text-xs text-zinc-400 capitalize">{key.replace(/_/g, " ")}</span>
                                    <span className="text-xs font-mono text-zinc-100">{value}</span>

                                </div>
                            ))}
                        </div>
                    </div>

                    {/* AI Analysis */}
                    <div className="border border-zinc-700 rounded-lg px-3 py-2.5 flex flex-col gap-2">
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 rounded-full bg-blue-950 flex items-center justify-center flex-shrink-0">
                                <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                                    <circle cx="5" cy="5" r="4" stroke="#185FA5" strokeWidth="1" />
                                    <path d="M5 4v3M5 3v.5" stroke="#185FA5" strokeWidth="1" strokeLinecap="round" />
                                </svg>
                            </div>
                            <p className="text-xs text-zinc-400 uppercase tracking-wide">AI analysis</p>
                        </div>
                        <p className="text-sm text-zinc-100 leading-relaxed">
                            {event.analysis ?? "No analysis available."}
                        </p>
                    </div>

                </div>
            </div>
        </div>
    );
};


export default function Firewall() {
    return (
        <div className="p-5">
            <Alerts />
        </div>
    );
}