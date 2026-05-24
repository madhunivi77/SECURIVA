import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Search,
  LayoutGrid,
  List,
  ChevronDown,
  Bell,
  MessageSquare,
  ScrollText,
  Activity,
  SlidersHorizontal,
  ArrowUpRight,
} from "lucide-react";

const MONO =
  '"Geist Mono", ui-monospace, SFMono-Regular, "SF Mono", Menlo, monospace';

function formatRelativeTime(value) {
  if (!value) return "";
  const ts = typeof value === "number" ? value : Date.parse(value);
  if (!Number.isFinite(ts)) return "";
  const diff = Date.now() - ts;
  if (diff < 0) return "just now";
  const sec = Math.floor(diff / 1000);
  if (sec < 60) return "just now";
  const min = Math.floor(sec / 60);
  if (min < 60) return `${min}m ago`;
  const hr = Math.floor(min / 60);
  if (hr < 24) return `${hr}h ago`;
  const day = Math.floor(hr / 24);
  if (day < 7) return `${day}d ago`;
  return new Date(ts).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
}

function prettyEventLabel(log) {
  const raw = log.message || log.event || log.action || log.type || "Event";
  const str = String(raw).replace(/_/g, " ").trim();
  if (!str) return "Event";
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export default function Home() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [view, setView] = useState("grid");
  const [stats, setStats] = useState({ integrations: 0, chats: 0, activity: 0 });
  const [recentChats, setRecentChats] = useState([]);
  const [recentLogs, setRecentLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      await Promise.allSettled([
        fetch("/api/composio/connections", { credentials: "include" })
          .then((r) => (r.ok ? r.json() : null))
          .then((d) => {
            if (!d) return;
            const connected = (d.connections || []).filter(
              (c) => !c.status || c.status === "ACTIVE"
            );
            setStats((s) => ({ ...s, integrations: connected.length }));
          }),
        fetch("/chat/list", { credentials: "include" })
          .then((r) => (r.ok ? r.json() : null))
          .then((d) => {
            if (!d) return;
            const list = d.conversations || [];
            setRecentChats(list.slice(0, 4));
            setStats((s) => ({ ...s, chats: list.length }));
          }),
        fetch("/api/logs?limit=20", { credentials: "include" })
          .then((r) => (r.ok ? r.json() : null))
          .then((d) => {
            if (!d) return;
            const list = d.logs || [];
            setRecentLogs(list.slice(0, 5));
            setStats((s) => ({ ...s, activity: list.length }));
          }),
      ]);
      setLoading(false);
    }
    load();
  }, []);

  const q = query.toLowerCase();
  const filteredChats = recentChats.filter((c) => {
    if (!q) return true;
    const title = (c.title || c.first_message || "").toLowerCase();
    return title.includes(q);
  });

  const chatLimit = 100;
  const usagePercent = Math.min(
    100,
    Math.round((stats.chats / chatLimit) * 100)
  );

  return (
    <div className="min-h-full">
      {/* Toolbar */}
      <div
        className="px-4 py-3 flex items-center gap-1.5"
        style={{ borderBottom: "1px solid var(--border)" }}
      >
        <div
          className="flex-1 flex items-center gap-2 h-8 px-2.5 rounded-md transition-colors"
          style={{
            background: "rgba(255, 255, 255, 0.02)",
            border: "1px solid var(--border)",
          }}
        >
          <Search className="w-3.5 h-3.5 shrink-0" style={{ color: "var(--ink-soft)" }} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="search chats..."
            className="flex-1 bg-transparent outline-none text-[12px]"
            style={{ color: "var(--ink)" }}
          />
        </div>

        <button className="sv-ghost w-8 justify-center px-0" aria-label="Filter">
          <SlidersHorizontal className="w-3.5 h-3.5" />
        </button>

        <div
          className="flex h-8 rounded-md overflow-hidden"
          style={{ border: "1px solid var(--border)", background: "rgba(255, 255, 255, 0.02)" }}
        >
          <ViewBtn active={view === "grid"} onClick={() => setView("grid")}>
            <LayoutGrid className="w-3.5 h-3.5" />
          </ViewBtn>
          <ViewBtn active={view === "list"} onClick={() => setView("list")} divider>
            <List className="w-3.5 h-3.5" />
          </ViewBtn>
        </div>

        <button onClick={() => navigate("/dashboard/chat")} className="sv-cta">
          <span>Add new</span>
          <ChevronDown className="w-3 h-3 opacity-80" strokeWidth={2.5} />
        </button>
      </div>

      {/* Two-column */}
      <div className="px-4 py-5 grid grid-cols-1 lg:grid-cols-5 gap-4">
        <div className="lg:col-span-2 space-y-4">
          <section>
            <Eyebrow>Usage</Eyebrow>
            <Card>
              <div className="px-4 pt-4 pb-3 flex items-start justify-between">
                <div>
                  <div className="text-[12.5px]" style={{ color: "var(--ink)" }}>
                    current_cycle
                  </div>
                  <div className="text-[10.5px] mt-0.5 uppercase tracking-[0.14em]" style={{ color: "var(--ink-soft)" }}>
                    resets monthly
                  </div>
                </div>
                <button
                  onClick={() => navigate("/dashboard/integrations")}
                  className="text-[11px] uppercase tracking-[0.14em] transition-colors"
                  style={{ color: "var(--ink-muted)" }}
                  onMouseEnter={(e) => (e.currentTarget.style.color = "var(--securiva-red)")}
                  onMouseLeave={(e) => (e.currentTarget.style.color = "var(--ink-muted)")}
                >
                  Billing →
                </button>
              </div>
              <div className="px-4 pb-4">
                <div className="flex items-end justify-between mb-2">
                  <div className="flex items-baseline gap-2">
                    <span
                      className="text-[44px] leading-none tabular-nums"
                      style={{
                        fontFamily: MONO,
                        fontWeight: 500,
                        color: "var(--ink)",
                        letterSpacing: "-0.02em",
                      }}
                    >
                      {stats.chats}
                    </span>
                    <span
                      className="text-[12px] tabular-nums"
                      style={{ color: "var(--ink-soft)" }}
                    >
                      / {chatLimit} chats
                    </span>
                  </div>
                  <span
                    className="text-[11px] tabular-nums uppercase tracking-[0.12em]"
                    style={{ color: "var(--ink-soft)", fontFamily: MONO }}
                  >
                    {usagePercent}%
                  </span>
                </div>
                <div
                  className="h-[3px] rounded-full overflow-hidden"
                  style={{ background: "var(--border)" }}
                >
                  <div
                    className="h-full transition-all duration-500"
                    style={{
                      width: `${usagePercent}%`,
                      background: "var(--securiva-red)",
                      boxShadow: "0 0 8px -1px rgba(239, 68, 68, 0.8)",
                    }}
                  />
                </div>
              </div>
              <UsageRow label="Connected integrations" value={stats.integrations} />
              <UsageRow label="Activity events" value={stats.activity} />
            </Card>
          </section>

          <section>
            <Eyebrow>Alerts</Eyebrow>
            <Card>
              <div className="p-5 flex flex-col items-center text-center">
                <div
                  className="w-9 h-9 rounded-md flex items-center justify-center mb-3"
                  style={{
                    background: "var(--securiva-red-dim)",
                    border: "1px solid rgba(239, 68, 68, 0.35)",
                  }}
                >
                  <Bell className="w-4 h-4" style={{ color: "var(--securiva-red)" }} strokeWidth={1.75} />
                </div>
                <div
                  className="text-[14px] mb-1"
                  style={{ color: "var(--ink)", fontWeight: 500, letterSpacing: "-0.01em" }}
                >
                  Stay on top of failures
                </div>
                <p
                  className="text-[11.5px] mb-4 max-w-[240px] leading-relaxed"
                  style={{ color: "var(--ink-muted)" }}
                >
                  Get notified when a tool call errors or an integration disconnects.
                </p>
                <button className="sv-cta">Enable notifications</button>
              </div>
            </Card>
          </section>
        </div>

        <div className="lg:col-span-3">
          <div className="flex items-center justify-between mb-2.5">
            <Eyebrow inline>Chats</Eyebrow>
            <button
              onClick={() => navigate("/dashboard/chat")}
              className="text-[11px] uppercase tracking-[0.14em] transition-colors"
              style={{ color: "var(--ink-muted)" }}
              onMouseEnter={(e) => (e.currentTarget.style.color = "var(--securiva-red)")}
              onMouseLeave={(e) => (e.currentTarget.style.color = "var(--ink-muted)")}
            >
              View all →
            </button>
          </div>

          {loading ? (
            <Card>
              <div className="p-8 text-center text-[11.5px] uppercase tracking-[0.14em]" style={{ color: "var(--ink-soft)" }}>
                Loading…
              </div>
            </Card>
          ) : filteredChats.length === 0 ? (
            <Card>
              <div className="p-10 flex flex-col items-center text-center">
                <div
                  className="w-9 h-9 rounded-md flex items-center justify-center mb-3"
                  style={{ background: "var(--bg-elev-2)", border: "1px solid var(--border)" }}
                >
                  <MessageSquare className="w-4 h-4" style={{ color: "var(--ink-muted)" }} strokeWidth={1.75} />
                </div>
                <div
                  className="text-[14px] mb-1"
                  style={{ color: "var(--ink)", fontWeight: 500 }}
                >
                  {query ? "No matches" : "No chats yet"}
                </div>
                <p className="text-[11.5px] mb-4 max-w-[280px]" style={{ color: "var(--ink-muted)" }}>
                  {query
                    ? `Nothing matches "${query}".`
                    : "Start a conversation and it will appear here."}
                </p>
                {!query && (
                  <button onClick={() => navigate("/dashboard/chat")} className="sv-cta">
                    Start a chat
                  </button>
                )}
              </div>
            </Card>
          ) : (
            <div
              className={
                view === "grid"
                  ? "grid grid-cols-1 sm:grid-cols-2 gap-3"
                  : "space-y-2"
              }
            >
              {filteredChats.map((c) => (
                <ChatCard
                  key={c.id || c.conversation_id || c.title}
                  chat={c}
                  onOpen={() =>
                    navigate("/dashboard/chat", {
                      state: { conversationId: c.id || c.conversation_id },
                    })
                  }
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Recent activity */}
      <div className="px-4 pb-8">
        <div className="flex items-center justify-between mb-2.5">
          <Eyebrow inline>Recent activity</Eyebrow>
          <button
            onClick={() => navigate("/dashboard/logs")}
            className="text-[11px] uppercase tracking-[0.14em] transition-colors"
            style={{ color: "var(--ink-muted)" }}
            onMouseEnter={(e) => (e.currentTarget.style.color = "var(--securiva-red)")}
            onMouseLeave={(e) => (e.currentTarget.style.color = "var(--ink-muted)")}
          >
            View logs →
          </button>
        </div>
        <Card>
          {loading ? (
            <div className="p-10 text-center text-[11.5px] uppercase tracking-[0.14em]" style={{ color: "var(--ink-soft)" }}>
              Loading…
            </div>
          ) : recentLogs.length === 0 ? (
            <div className="p-10 flex flex-col items-center text-center">
              <div
                className="w-9 h-9 rounded-md flex items-center justify-center mb-3"
                style={{ background: "var(--bg-elev-2)", border: "1px solid var(--border)" }}
              >
                <ScrollText className="w-4 h-4" style={{ color: "var(--ink-muted)" }} strokeWidth={1.75} />
              </div>
              <div className="text-[14px] mb-1" style={{ color: "var(--ink)", fontWeight: 500 }}>
                No activity yet
              </div>
              <p className="text-[11.5px] max-w-[340px]" style={{ color: "var(--ink-muted)" }}>
                Chat and integration events will appear here as you use the agent.
              </p>
            </div>
          ) : (
            <ul>
              {recentLogs.map((log, i) => (
                <li
                  key={i}
                  className="px-4 h-11 flex items-center justify-between gap-3"
                  style={i > 0 ? { borderTop: "1px solid var(--border)" } : undefined}
                >
                  <div className="flex items-center gap-2.5 min-w-0 flex-1">
                    <Activity
                      className="w-3.5 h-3.5 shrink-0"
                      style={{ color: "var(--securiva-red)" }}
                      strokeWidth={2}
                    />
                    <span className="text-[12px] truncate" style={{ color: "var(--ink)" }}>
                      {prettyEventLabel(log)}
                    </span>
                  </div>
                  <span
                    className="text-[10.5px] shrink-0 tabular-nums uppercase tracking-[0.12em]"
                    style={{ color: "var(--ink-soft)", fontFamily: MONO }}
                  >
                    {formatRelativeTime(log.timestamp || log.created_at) ||
                      log.timestamp ||
                      log.created_at}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}

function Card({ children }) {
  return (
    <div
      className="rounded-lg overflow-hidden"
      style={{
        background: "var(--bg-elev)",
        border: "1px solid var(--border)",
      }}
    >
      {children}
    </div>
  );
}

function Eyebrow({ children, inline }) {
  return (
    <h3
      className={`text-[10.5px] uppercase tracking-[0.22em] ${inline ? "" : "mb-2.5"}`}
      style={{ color: "var(--ink-soft)", fontWeight: 500 }}
    >
      {children}
    </h3>
  );
}

function ViewBtn({ active, onClick, children, divider }) {
  return (
    <button
      onClick={onClick}
      className="w-8 flex items-center justify-center transition-colors"
      style={{
        background: active ? "var(--bg-elev)" : "transparent",
        color: active ? "var(--ink)" : "var(--ink-soft)",
        borderLeft: divider ? "1px solid var(--border)" : undefined,
      }}
    >
      {children}
    </button>
  );
}

function UsageRow({ label, value }) {
  return (
    <div
      className="px-4 h-11 flex items-center justify-between"
      style={{ borderTop: "1px solid var(--border)" }}
    >
      <span className="text-[11.5px] uppercase tracking-[0.14em]" style={{ color: "var(--ink-muted)" }}>
        {label}
      </span>
      <span
        className="text-[12.5px] tabular-nums"
        style={{ color: "var(--ink)", fontFamily: MONO, fontWeight: 500 }}
      >
        {value}
      </span>
    </div>
  );
}

function ChatCard({ chat, onOpen }) {
  const title = chat.title || chat.first_message || "Untitled chat";
  const ts = chat.updated_at || chat.created_at || "";
  const relative = formatRelativeTime(ts);

  return (
    <button
      onClick={onOpen}
      className="group text-left rounded-lg p-4 transition-all"
      style={{ background: "var(--bg-elev)", border: "1px solid var(--border)" }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = "var(--securiva-red)";
        e.currentTarget.style.background = "var(--bg-elev-2)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = "var(--border)";
        e.currentTarget.style.background = "var(--bg-elev)";
      }}
    >
      <div className="flex items-start gap-3">
        <div
          className="w-8 h-8 rounded-md flex items-center justify-center shrink-0"
          style={{
            background: "var(--bg-deep)",
            border: "1px solid var(--border)",
          }}
        >
          <MessageSquare
            className="w-[15px] h-[15px]"
            style={{ color: "var(--ink-muted)" }}
            strokeWidth={1.75}
          />
        </div>
        <div className="min-w-0 flex-1">
          <div className="text-[12.5px] truncate" style={{ color: "var(--ink)", fontWeight: 500 }}>
            {title}
          </div>
          <div
            className="text-[10.5px] mt-0.5 uppercase tracking-[0.12em]"
            style={{ color: "var(--ink-soft)", fontFamily: MONO }}
          >
            {relative || "never updated"}
          </div>
        </div>
        <ArrowUpRight
          className="w-3.5 h-3.5 shrink-0 transition-colors"
          style={{ color: "var(--ink-soft)" }}
          strokeWidth={2}
        />
      </div>
    </button>
  );
}
