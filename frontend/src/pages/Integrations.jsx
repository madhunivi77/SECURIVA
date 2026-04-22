import { useEffect, useState } from "react";
import { Check, Loader2, Plus, Search } from "lucide-react";

function ToolkitCard({ toolkit, connected, pending, error, onConnect }) {
  const { name, slug, description, logo, categories, tools_count } = toolkit;
  const primaryCategory = (categories && categories[0]) || "";
  return (
    <div
      className="group rounded-lg p-4 transition-all flex flex-col"
      style={{ background: "var(--bg-elev)", border: "1px solid var(--ivory-3)" }}
      onMouseEnter={(e) => (e.currentTarget.style.borderColor = "var(--securiva-red)")}
      onMouseLeave={(e) => (e.currentTarget.style.borderColor = "var(--ivory-3)")}
    >
      <div className="flex items-start gap-3">
        {logo ? (
          <img
            src={logo}
            alt=""
            className="w-8 h-8 rounded-md object-contain shrink-0 p-1"
            style={{ background: "var(--ivory-2)", border: "1px solid var(--ivory-3)" }}
            onError={(e) => { e.currentTarget.style.display = "none"; }}
          />
        ) : (
          <div
            className="w-8 h-8 rounded-md shrink-0"
            style={{ background: "var(--ivory-2)", border: "1px solid var(--ivory-3)" }}
          />
        )}
        <div className="min-w-0 flex-1">
          <div className="flex items-baseline gap-2 flex-wrap">
            <h3 className="text-[13px] font-semibold truncate" style={{ color: "var(--ink)" }}>{name}</h3>
            {primaryCategory && (
              <span
                className="text-[9.5px] uppercase tracking-[0.08em] font-medium"
                style={{ color: "var(--ink-soft)" }}
              >
                {primaryCategory}
              </span>
            )}
          </div>
          <p className="text-[12px] mt-1 line-clamp-2 leading-relaxed" style={{ color: "var(--ink-muted)" }}>
            {description}
          </p>
        </div>
      </div>
      <div className="mt-3.5 flex items-center justify-between gap-2">
        <span className="text-[11px] truncate font-mono" style={{ color: "var(--ink-soft)" }}>
          {slug}{tools_count ? ` · ${Math.round(tools_count)} tools` : ""}
        </span>
        {connected ? (
          <span
            className="inline-flex items-center gap-1 text-[11.5px] font-medium shrink-0"
            style={{ color: "var(--securiva-red)" }}
          >
            <Check className="w-3.5 h-3.5" />
            Connected
          </span>
        ) : (
          <button
            disabled={pending}
            onClick={() => onConnect(toolkit)}
            className="sv-cta disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
            style={{ height: "28px", fontSize: "11.5px", paddingLeft: "10px", paddingRight: "10px" }}
          >
            {pending ? <Loader2 className="w-3 h-3 animate-spin" /> : <Plus className="w-3 h-3" />}
            {pending ? "Opening…" : "Connect"}
          </button>
        )}
      </div>
      {error && (
        <p className="mt-2 text-[11.5px]" style={{ color: "var(--securiva-red)" }}>{error}</p>
      )}
    </div>
  );
}

export default function Integrations() {
  const [query, setQuery] = useState("");
  const [toolkits, setToolkits] = useState([]);
  const [toolkitsLoading, setToolkitsLoading] = useState(true);
  const [toolkitsError, setToolkitsError] = useState(null);
  const [connected, setConnected] = useState(new Set());
  const [pending, setPending] = useState(new Set());
  const [errors, setErrors] = useState({});

  const loadToolkits = async () => {
    setToolkitsLoading(true);
    setToolkitsError(null);
    try {
      const res = await fetch("/api/composio/toolkits?limit=200", { credentials: "include" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setToolkits(data.toolkits || []);
    } catch (err) {
      setToolkitsError(err.message);
    } finally {
      setToolkitsLoading(false);
    }
  };

  const loadConnections = async () => {
    try {
      const res = await fetch("/api/composio/connections", { credentials: "include" });
      if (!res.ok) return;
      const data = await res.json();
      const slugs = new Set(
        (data.connections || [])
          .filter((c) => c.status === "ACTIVE" || !c.status)
          .map((c) => c.toolkit)
          .filter(Boolean)
      );
      setConnected(slugs);
    } catch (err) {
      console.error("Failed to load connections", err);
    }
  };

  useEffect(() => {
    loadToolkits();
    loadConnections();
    const onFocus = () => loadConnections();
    window.addEventListener("focus", onFocus);
    return () => window.removeEventListener("focus", onFocus);
  }, []);

  const handleConnect = async (toolkit) => {
    setErrors((prev) => ({ ...prev, [toolkit.slug]: null }));
    setPending((prev) => new Set(prev).add(toolkit.slug));
    try {
      const res = await fetch("/api/composio/connect", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ toolkit: toolkit.slug }),
      });
      const data = await res.json();
      if (!res.ok || !data.redirect_url) {
        throw new Error(data.error || "Failed to get OAuth URL");
      }
      window.open(data.redirect_url, "_blank", "noopener,noreferrer");
    } catch (err) {
      setErrors((prev) => ({ ...prev, [toolkit.slug]: err.message }));
    } finally {
      setPending((prev) => {
        const next = new Set(prev);
        next.delete(toolkit.slug);
        return next;
      });
    }
  };

  const q = query.toLowerCase();
  const filtered = toolkits.filter((t) => {
    if (!q) return true;
    if (t.name && t.name.toLowerCase().includes(q)) return true;
    if (t.slug && t.slug.toLowerCase().includes(q)) return true;
    if (t.description && t.description.toLowerCase().includes(q)) return true;
    if (t.categories && t.categories.some((c) => c && c.toLowerCase().includes(q))) return true;
    return false;
  });

  const connectedCount = connected.size;

  return (
    <div className="min-h-full">
      <div className="max-w-6xl mx-auto px-6 py-6">
        <header className="mb-5">
          <div className="flex items-baseline gap-3">
            <h1
              className="text-[22px] uppercase leading-none"
              style={{
                fontFamily: "var(--font-mono)",
                fontWeight: 500,
                color: "var(--ink)",
                letterSpacing: "0.14em",
              }}
            >
              Integrations
            </h1>
            <span className="text-[12.5px] tabular-nums" style={{ color: "var(--ink-soft)" }}>
              {connectedCount}/{toolkits.length || "—"} connected
            </span>
          </div>
          <p className="text-[12.5px] mt-1.5 max-w-2xl leading-relaxed" style={{ color: "var(--ink-muted)" }}>
            Connect third-party apps so the agent can act on your behalf. Authorization is handled by Composio; tokens stay in their vault, not ours.
          </p>
        </header>

        <div
          className="mb-4 flex items-center gap-2 rounded-md h-9 px-3 transition-colors"
          style={{ background: "var(--bg-elev)", border: "1px solid var(--ivory-3)" }}
        >
          <Search className="w-3.5 h-3.5" style={{ color: "var(--ink-soft)" }} />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Filter by name or category…"
            className="bg-transparent flex-1 outline-none text-[12.5px]"
            style={{ color: "var(--ink)" }}
          />
        </div>

        {toolkitsLoading && (
          <p className="text-[12.5px] text-center py-12" style={{ color: "var(--ink-soft)" }}>Loading toolkits…</p>
        )}
        {toolkitsError && (
          <p className="text-[12.5px] text-center py-12" style={{ color: "var(--securiva-red)" }}>
            Failed to load toolkits: {toolkitsError}
          </p>
        )}
        {!toolkitsLoading && !toolkitsError && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {filtered.map((t) => (
              <ToolkitCard
                key={t.slug}
                toolkit={t}
                connected={connected.has(t.slug)}
                pending={pending.has(t.slug)}
                error={errors[t.slug]}
                onConnect={handleConnect}
              />
            ))}
          </div>
        )}

        {!toolkitsLoading && !toolkitsError && filtered.length === 0 && (
          <p className="text-[12.5px] mt-8 text-center" style={{ color: "var(--ink-soft)" }}>
            No toolkits match "{query}"
          </p>
        )}

        {connectedCount > 0 && (
          <p className="mt-6 text-[11.5px]" style={{ color: "var(--ink-soft)" }}>
            Tip: refocus this tab after authorizing to refresh connection status.
          </p>
        )}

        <footer
          className="mt-10 pt-5 text-[11.5px]"
          style={{ borderTop: "1px solid var(--ivory-3)", color: "var(--ink-soft)" }}
        >
          Powered by Composio · 500+ apps available via the agent.
        </footer>
      </div>
    </div>
  );
}
