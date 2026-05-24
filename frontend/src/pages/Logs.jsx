import { useState, useEffect, Fragment, useRef } from "react";
import {
  Search,
  RotateCw,
  ChevronRight,
  AlertTriangle,
  ShieldCheck,
} from "lucide-react";

/* ──────────────────────────────────────────────────────────────
   Activity Logs — Industrial Ledger
   Mono-first · monochrome codes · red only for faults
   ────────────────────────────────────────────────────────────── */

const MONO =
  '"Geist Mono", ui-monospace, SFMono-Regular, "SF Mono", Menlo, monospace';

// Event codes — terminal-log style, not pastel pills
const EVENT_META = {
  signin: { code: "SGN", label: "Sign in", glyph: "↳" },
  logout: { code: "OUT", label: "Logout", glyph: "↲" },
  chat: { code: "CHT", label: "Chat", glyph: "•" },
  tool_call: { code: "TLC", label: "Tool call", glyph: "⊸" },
  voice_session: { code: "VCE", label: "Voice", glyph: "◐" },
  sms: { code: "SMS", label: "SMS", glyph: "≋" },
  salesforce_connect: { code: "SFC", label: "Salesforce", glyph: "⌁" },
  error: { code: "ERR", label: "Error", glyph: "✕" },
};

const EVENT_FILTERS = [
  { value: "", label: "All" },
  { value: "signin", label: "Sign in" },
  { value: "chat", label: "Chat" },
  { value: "tool_call", label: "Tool" },
  { value: "voice_session", label: "Voice" },
  { value: "sms", label: "SMS" },
];

function formatTimestamp(ts) {
  if (!ts) return "—";
  const d = new Date(ts.includes("Z") ? ts : ts + "Z");
  if (Number.isNaN(d.getTime())) return ts;
  // 04-18 · 14:07:32.441 — date separator · time with ms
  const pad = (n, w = 2) => String(n).padStart(w, "0");
  const mo = pad(d.getMonth() + 1);
  const da = pad(d.getDate());
  const hh = pad(d.getHours());
  const mm = pad(d.getMinutes());
  const ss = pad(d.getSeconds());
  const ms = pad(d.getMilliseconds(), 3);
  return `${mo}-${da} · ${hh}:${mm}:${ss}.${ms}`;
}

function describe(log) {
  const d = log.details || {};
  switch (log.event) {
    case "signin":
      return `${d.method === "google_oauth" ? "google" : "local"} auth${
        log.user_email ? ` — ${log.user_email}` : ""
      }`;
    case "logout":
      return log.user_email || "session terminated";
    case "chat":
      return d.user_message
        ? d.user_message.slice(0, 110) +
            (d.user_message.length > 110 ? "…" : "")
        : `${d.model || "llm"} · ${d.tool_calls_count || 0} tool calls`;
    case "tool_call":
      return d.tool_name || "unknown tool";
    case "voice_session":
      return "voice session opened";
    case "sms":
      return `→ ${d.phone || "unknown"}`;
    default:
      return log.error || JSON.stringify(d).slice(0, 100);
  }
}

export default function Logs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [onlyErrors, setOnlyErrors] = useState(false);
  const [eventFilter, setEventFilter] = useState("");
  const [search, setSearch] = useState("");
  const [expandedRow, setExpandedRow] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  // Debounced search
  const searchTimer = useRef(null);
  const [debouncedSearch, setDebouncedSearch] = useState("");

  useEffect(() => {
    if (searchTimer.current) clearTimeout(searchTimer.current);
    searchTimer.current = setTimeout(() => setDebouncedSearch(search), 250);
    return () => clearTimeout(searchTimer.current);
  }, [search]);

  const fetchLogs = async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);
    try {
      const params = new URLSearchParams();
      if (onlyErrors) params.set("status", "error");
      if (eventFilter) params.set("event", eventFilter);
      if (debouncedSearch) params.set("search", debouncedSearch);

      const res = await fetch(`/api/logs?${params.toString()}`, {
        credentials: "include",
      });
      if (res.ok) {
        const data = await res.json();
        setLogs(data.logs || []);
      }
    } catch (err) {
      console.error("Failed to fetch logs:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [onlyErrors, eventFilter, debouncedSearch]);

  const errorCount = logs.filter((l) => l.status === "error").length;

  return (
    <div className="min-h-full">
      {/* Header band */}
      <header className="px-6 pt-6 pb-5 relative">
        <div className="flex items-baseline justify-between gap-4 flex-wrap">
          <div className="flex items-baseline gap-3">
            <h1
              className="text-[22px] uppercase leading-none"
              style={{
                fontFamily: MONO,
                fontWeight: 500,
                color: "var(--ink)",
                letterSpacing: "0.14em",
              }}
            >
              Activity
            </h1>
            <span
              className="text-[11px] uppercase tracking-[0.18em]"
              style={{ color: "var(--ink-soft)", fontFamily: MONO }}
            >
              {loading ? "—" : logs.length} events
              {errorCount > 0 && (
                <span style={{ color: "var(--securiva-red)", marginLeft: 10 }}>
                  · {errorCount} fault{errorCount === 1 ? "" : "s"}
                </span>
              )}
            </span>
          </div>

          <button
            onClick={() => fetchLogs(true)}
            className="sv-ghost"
            style={{ height: "32px", fontSize: "12px" }}
          >
            <RotateCw
              className={`w-3.5 h-3.5 ${refreshing ? "animate-spin" : ""}`}
              strokeWidth={2}
            />
            Refresh
          </button>
        </div>
        {/* red hairline — matches site's mono-tech accent */}
        <div
          className="absolute left-0 right-0 bottom-0"
          style={{
            height: 1,
            background:
              "linear-gradient(to right, transparent 0%, rgba(239, 68, 68, 0) 10%, rgba(239, 68, 68, 0.5) 50%, rgba(239, 68, 68, 0) 90%, transparent 100%)",
          }}
        />
      </header>

      {/* Filter strip */}
      <div className="px-6 py-3 flex items-center gap-2 flex-wrap">
        {/* Search */}
        <div
          className="flex items-center gap-2 h-8 px-2.5 rounded-md transition-colors flex-1 min-w-[220px] max-w-[360px]"
          style={{
            background: "var(--bg-deep)",
            border: "1px solid var(--border)",
          }}
        >
          <Search
            className="w-3.5 h-3.5 shrink-0"
            style={{ color: "var(--ink-soft)" }}
          />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder='user@email · tool_name · "error"'
            className="flex-1 bg-transparent outline-none text-[12.5px] min-w-0"
            style={{ color: "var(--ink)", fontFamily: MONO }}
          />
        </div>

        {/* Event chips */}
        <div
          className="flex items-center gap-0 h-8 rounded-md overflow-hidden"
          style={{
            background: "var(--bg-deep)",
            border: "1px solid var(--border)",
          }}
        >
          {EVENT_FILTERS.map((f, i) => {
            const active = eventFilter === f.value;
            return (
              <button
                key={f.value}
                onClick={() => setEventFilter(f.value)}
                className="px-2.5 h-full text-[11.5px] transition-colors"
                style={{
                  background: active ? "var(--bg-elev)" : "transparent",
                  color: active ? "var(--ink)" : "var(--ink-soft)",
                  fontWeight: active ? 500 : 400,
                  borderLeft: i > 0 ? "1px solid var(--border)" : undefined,
                  boxShadow: active
                    ? "inset 0 -1px 0 var(--securiva-red)"
                    : "none",
                }}
              >
                {f.label}
              </button>
            );
          })}
        </div>

        {/* Errors-only toggle */}
        <button
          onClick={() => setOnlyErrors((v) => !v)}
          className="flex items-center gap-1.5 h-8 px-3 rounded-md text-[11.5px] transition-colors"
          style={{
            border: onlyErrors
              ? "1px solid var(--securiva-red)"
              : "1px solid var(--border)",
            background: onlyErrors
              ? "var(--securiva-red-dim)"
              : "var(--bg-deep)",
            color: onlyErrors ? "var(--securiva-red)" : "var(--ink-muted)",
            fontWeight: onlyErrors ? 500 : 400,
            boxShadow: onlyErrors
              ? "0 0 0 1px rgba(239, 68, 68, 0.18), 0 6px 18px -10px rgba(239, 68, 68, 0.6)"
              : "none",
            fontFamily: MONO,
          }}
        >
          <AlertTriangle className="w-3.5 h-3.5" strokeWidth={2} />
          Errors only
        </button>
      </div>

      {/* Ledger */}
      <div className="px-6 pb-10">
        {loading ? (
          <LedgerState text="Reading the log…" />
        ) : logs.length === 0 ? (
          <LedgerState
            title={onlyErrors ? "Nothing broken" : "No activity yet"}
            text={
              onlyErrors
                ? "No faults recorded under the current filter."
                : "Chat, voice, and tool events will land here as they happen."
            }
            icon={
              onlyErrors ? (
                <ShieldCheck className="w-4 h-4" style={{ color: "var(--ink-muted)" }} />
              ) : undefined
            }
          />
        ) : (
          <div
            className="rounded-lg overflow-hidden"
            style={{
              background: "var(--bg-elev)",
              border: "1px solid var(--border)",
            }}
          >
            <table className="w-full text-left" style={{ tableLayout: "fixed" }}>
              <colgroup>
                <col style={{ width: 180 }} />
                <col style={{ width: 86 }} />
                <col />
                <col style={{ width: 96 }} />
                <col style={{ width: 180 }} />
                <col style={{ width: 22 }} />
              </colgroup>
              <thead>
                <tr
                  style={{
                    borderBottom: "1px solid var(--border)",
                    background: "var(--bg-deep)",
                  }}
                >
                  {[
                    "Timestamp",
                    "Event",
                    "Detail",
                    "Status",
                    "User",
                    "",
                  ].map((h, i) => (
                    <th
                      key={i}
                      className="px-4 py-2 text-[10px] font-medium uppercase tracking-[0.14em]"
                      style={{ color: "var(--ink-soft)" }}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {logs.map((log, i) => {
                  const isError = log.status === "error";
                  const isOpen = expandedRow === i;
                  const meta =
                    EVENT_META[log.event] || {
                      code: log.event?.slice(0, 3).toUpperCase() || "—",
                      label: log.event || "—",
                      glyph: "·",
                    };
                  return (
                    <Fragment key={i}>
                      <tr
                        onClick={() => setExpandedRow(isOpen ? null : i)}
                        className="log-row cursor-pointer"
                        style={{
                          borderBottom: "1px solid var(--border-soft)",
                          borderLeft: isError
                            ? "2px solid var(--securiva-red)"
                            : "2px solid transparent",
                          background: isOpen
                            ? "var(--bg-elev-2)"
                            : "transparent",
                          animation: `log-row-in 420ms cubic-bezier(0.16, 1, 0.3, 1) ${Math.min(
                            i,
                            12
                          ) * 28}ms both`,
                        }}
                      >
                        <td
                          className="px-4 py-2.5 whitespace-nowrap"
                          style={{
                            color: "var(--ink-muted)",
                            fontFamily: MONO,
                            fontSize: "11.5px",
                            fontVariantNumeric: "tabular-nums",
                          }}
                        >
                          {formatTimestamp(log.timestamp)}
                        </td>
                        <td className="px-4 py-2.5">
                          <span
                            className="inline-flex items-center gap-1.5"
                            style={{
                              fontFamily: MONO,
                              fontSize: "10.5px",
                              letterSpacing: "0.08em",
                              color: isError
                                ? "var(--securiva-red)"
                                : "var(--ink-muted)",
                              textTransform: "uppercase",
                            }}
                          >
                            <span
                              style={{
                                display: "inline-block",
                                width: 12,
                                fontSize: "11px",
                                lineHeight: 1,
                                color: isError
                                  ? "var(--securiva-red)"
                                  : "var(--ink-soft)",
                              }}
                            >
                              {meta.glyph}
                            </span>
                            {meta.code}
                          </span>
                        </td>
                        <td
                          className="px-4 py-2.5 truncate"
                          style={{
                            color: isError ? "var(--securiva-red)" : "var(--ink)",
                            fontSize: "12.5px",
                          }}
                        >
                          {describe(log)}
                        </td>
                        <td className="px-4 py-2.5">
                          <StatusMark status={log.status} />
                        </td>
                        <td
                          className="px-4 py-2.5 truncate"
                          style={{
                            color: "var(--ink-soft)",
                            fontFamily: MONO,
                            fontSize: "11px",
                          }}
                        >
                          {log.user_email ||
                            log.user_id?.slice(0, 8) ||
                            "—"}
                        </td>
                        <td className="pr-3">
                          <ChevronRight
                            className="w-3.5 h-3.5 transition-transform"
                            style={{
                              color: "var(--ink-soft)",
                              transform: isOpen ? "rotate(90deg)" : "rotate(0)",
                            }}
                            strokeWidth={2}
                          />
                        </td>
                      </tr>
                      {isOpen && (
                        <tr
                          style={{
                            background: "var(--bg-deep)",
                            borderBottom: "1px solid var(--border)",
                            borderLeft: isError
                              ? "2px solid var(--securiva-red)"
                              : "2px solid transparent",
                          }}
                        >
                          <td colSpan={6} className="px-4 py-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <DetailPane title="Details">
                                <JsonBlock value={log.details} />
                              </DetailPane>
                              <DetailPane
                                title={log.error ? "Error" : log.event === "tool_call" ? "Result" : "Info"}
                                tone={log.error ? "error" : "default"}
                              >
                                {log.error ? (
                                  <div
                                    style={{
                                      color: "var(--securiva-red)",
                                      fontFamily: MONO,
                                      fontSize: "11.5px",
                                      lineHeight: 1.55,
                                      whiteSpace: "pre-wrap",
                                    }}
                                  >
                                    {log.error}
                                  </div>
                                ) : log.event === "tool_call" &&
                                  log.details?.result ? (
                                  <JsonBlock value={log.details.result} />
                                ) : (
                                  <div
                                    style={{
                                      color: "var(--ink-soft)",
                                      fontFamily: MONO,
                                      fontSize: "11.5px",
                                    }}
                                  >
                                    —
                                  </div>
                                )}
                              </DetailPane>
                              {log.metadata && (
                                <DetailPane title="Metadata" span={2}>
                                  <JsonBlock value={log.metadata} />
                                </DetailPane>
                              )}
                            </div>
                          </td>
                        </tr>
                      )}
                    </Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Footer count line */}
        {!loading && logs.length > 0 && (
          <div
            className="mt-3 flex items-center justify-between text-[10px] uppercase tracking-[0.18em]"
            style={{ color: "var(--ink-soft)", fontFamily: MONO }}
          >
            <span>{logs.length} entries · most recent first</span>
            <span>securiva · ledger</span>
          </div>
        )}
      </div>

      {/* keyframes for staggered row entry */}
      <style>{`
        @keyframes log-row-in {
          from { opacity: 0; transform: translateY(4px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .log-row:hover { background: var(--bg-hover) !important; }
      `}</style>
    </div>
  );
}

function StatusMark({ status }) {
  const isError = status === "error";
  return (
    <span
      className="inline-flex items-center gap-1.5"
      style={{
        fontFamily: MONO,
        fontSize: "10.5px",
        letterSpacing: "0.1em",
        textTransform: "uppercase",
        color: isError ? "var(--securiva-red)" : "var(--ink-muted)",
      }}
    >
      <span
        style={{
          width: 5,
          height: 5,
          borderRadius: 999,
          background: isError ? "var(--securiva-red)" : "#60a5fa",
          boxShadow: isError
            ? "0 0 0 3px rgba(239, 68, 68, 0.2)"
            : "0 0 0 3px rgba(96, 165, 250, 0.18)",
        }}
      />
      {isError ? "fault" : status || "ok"}
    </span>
  );
}

function DetailPane({ title, tone, span = 1, children }) {
  return (
    <div className={span === 2 ? "md:col-span-2" : undefined}>
      <div
        className="text-[10px] uppercase tracking-[0.14em] mb-1.5"
        style={{
          color: tone === "error" ? "var(--securiva-red)" : "var(--ink-soft)",
          fontFamily: MONO,
        }}
      >
        {title}
      </div>
      <div
        className="rounded-md p-3 overflow-auto"
        style={{
          background: "var(--bg-deep)",
          border: `1px solid ${
            tone === "error" ? "rgba(239, 68, 68, 0.35)" : "var(--border)"
          }`,
          maxHeight: 220,
        }}
      >
        {children}
      </div>
    </div>
  );
}

function JsonBlock({ value }) {
  return (
    <pre
      style={{
        margin: 0,
        fontFamily: MONO,
        fontSize: "11.5px",
        lineHeight: 1.55,
        color: "var(--ink)",
        whiteSpace: "pre-wrap",
        wordBreak: "break-word",
      }}
    >
      {value === undefined || value === null
        ? "—"
        : typeof value === "string"
        ? value
        : JSON.stringify(value, null, 2)}
    </pre>
  );
}

function LedgerState({ title, text, icon }) {
  return (
    <div
      className="rounded-lg py-14 flex flex-col items-center text-center"
      style={{
        background: "var(--bg-elev)",
        border: "1px solid var(--border)",
      }}
    >
      <div
        className="w-10 h-10 rounded-md flex items-center justify-center mb-3"
        style={{
          background: "var(--bg-deep)",
          border: "1px solid var(--border)",
        }}
      >
        {icon || (
          <Search
            className="w-4 h-4"
            style={{ color: "var(--ink-muted)" }}
            strokeWidth={1.75}
          />
        )}
      </div>
      {title && (
        <div
          className="text-[14px] leading-none mb-1.5"
          style={{
            color: "var(--ink)",
            fontWeight: 500,
            fontFamily: MONO,
            letterSpacing: "0.02em",
          }}
        >
          {title}
        </div>
      )}
      <p
        className="text-[12px] max-w-[340px] px-6"
        style={{ color: "var(--ink-muted)" }}
      >
        {text}
      </p>
    </div>
  );
}
