import { useEffect, useRef, useState } from "react";
import {
  House,
  MessageSquare,
  Mic,
  Plug,
  ScrollText,
  Settings,
  LogOut,
  Search,
  MoreHorizontal,
  Gauge,
  Sparkles,
} from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const PRIMARY_NAV = [
  { to: "/dashboard", label: "Overview", icon: House, end: true },
  { to: "/dashboard/chat", label: "Chat", icon: MessageSquare },
  { to: "/dashboard/voice", label: "Voice", icon: Mic },
  { to: "/dashboard/logs", label: "Activity", icon: ScrollText },
  { to: "/dashboard/integrations", label: "Integrations", icon: Plug },
];

const SECONDARY_NAV = [
  { label: "Usage", icon: Gauge },
  { label: "AI Gateway", icon: Sparkles },
];

function firstNameFromEmail(email) {
  if (!email) return "";
  const local = email.split("@")[0] || "";
  const first = local.split(/[._-]/)[0] || "";
  return first ? first.charAt(0).toUpperCase() + first.slice(1) : "";
}

export default function Sidebar() {
  const { logout, userEmail } = useAuth();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);
  const searchRef = useRef(null);
  const menuRef = useRef(null);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "f" && (e.metaKey || e.ctrlKey)) return;
      if (
        e.key === "f" &&
        document.activeElement?.tagName !== "INPUT" &&
        document.activeElement?.tagName !== "TEXTAREA"
      ) {
        e.preventDefault();
        searchRef.current?.focus();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    if (!menuOpen) return;
    const onClick = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [menuOpen]);

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  const q = query.trim().toLowerCase();
  const filteredPrimary = q
    ? PRIMARY_NAV.filter((n) => n.label.toLowerCase().includes(q))
    : PRIMARY_NAV;
  const filteredSecondary = q
    ? SECONDARY_NAV.filter((n) => n.label.toLowerCase().includes(q))
    : SECONDARY_NAV;

  const displayName = firstNameFromEmail(userEmail) || "Me";

  return (
    <aside
      className="w-[220px] shrink-0 flex flex-col relative z-[1]"
      style={{ background: "transparent" }}
    >
      {/* Brand */}
      <div className="px-3 pt-3 pb-2">
        <button
          className="w-full flex items-center gap-2 px-2 h-8 rounded-md transition-colors"
          style={{ color: "var(--ink)" }}
          onMouseEnter={(e) => (e.currentTarget.style.background = "var(--bg-hover)")}
          onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
        >
          <img
            src="/BlueLogoNoText.png"
            alt="Securiva"
            className="w-[22px] h-[22px] shrink-0 object-contain"
          />
          <span
            className="text-[13px] tracking-tight truncate"
            style={{ fontWeight: 500 }}
          >
            Securiva
          </span>
          <span
            className="ml-0.5 px-[5px] py-[1px] rounded text-[9px] font-semibold tracking-[0.1em] uppercase"
            style={{
              color: "var(--securiva-red)",
              background: "var(--securiva-red-dim)",
              border: "1px solid rgba(239, 68, 68, 0.35)",
            }}
          >
            Beta
          </span>
        </button>
      </div>

      {/* Search */}
      <div className="px-3 pb-2">
        <div
          className="group relative flex items-center gap-2 h-8 px-2 rounded-md transition-colors"
          style={{
            background: "rgba(255, 255, 255, 0.02)",
            border: "1px solid var(--border)",
          }}
        >
          <Search className="w-3.5 h-3.5 shrink-0" style={{ color: "var(--ink-soft)" }} />
          <input
            ref={searchRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="find..."
            className="flex-1 bg-transparent outline-none text-[12px] min-w-0"
            style={{ color: "var(--ink)" }}
          />
          <kbd
            className="text-[10px] rounded px-1 py-[1px] leading-none"
            style={{
              border: "1px solid var(--border)",
              background: "var(--bg-deep)",
              color: "var(--ink-soft)",
            }}
          >
            F
          </kbd>
        </div>
      </div>

      {/* Nav group eyebrow */}
      <div
        className="px-4 pt-1 pb-1 text-[9px] uppercase tracking-[0.2em]"
        style={{ color: "var(--ink-dim)" }}
      >
        Workspace
      </div>

      {/* Primary */}
      <nav className="flex-1 overflow-y-auto px-3 space-y-[1px]">
        {filteredPrimary.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className="group relative flex items-center gap-2.5 px-2 h-[30px] text-[12.5px] rounded-md transition-colors"
            style={({ isActive }) => ({
              background: isActive ? "var(--bg-elev)" : "transparent",
              color: isActive ? "var(--ink)" : "var(--ink-muted)",
              borderLeft: isActive
                ? "2px solid var(--securiva-red)"
                : "2px solid transparent",
              paddingLeft: isActive ? "6px" : "8px",
            })}
            onMouseEnter={(e) => {
              if (!e.currentTarget.getAttribute("aria-current")) {
                e.currentTarget.style.background = "var(--bg-hover)";
                e.currentTarget.style.color = "var(--ink)";
              }
            }}
            onMouseLeave={(e) => {
              if (!e.currentTarget.getAttribute("aria-current")) {
                e.currentTarget.style.background = "transparent";
                e.currentTarget.style.color = "var(--ink-muted)";
              }
            }}
          >
            <Icon className="w-[14px] h-[14px] shrink-0" strokeWidth={1.75} />
            <span className="truncate">{label}</span>
          </NavLink>
        ))}

        {filteredSecondary.length > 0 && (
          <>
            <div
              className="pt-5 pb-1 px-1 text-[9px] uppercase tracking-[0.2em]"
              style={{ color: "var(--ink-dim)" }}
            >
              Soon
            </div>
            {filteredSecondary.map(({ label, icon: Icon }) => (
              <div
                key={label}
                className="flex items-center gap-2.5 px-2 h-[30px] text-[12.5px] cursor-not-allowed rounded-md"
                style={{ color: "var(--ink-dim)" }}
              >
                <Icon className="w-[14px] h-[14px] shrink-0" strokeWidth={1.75} />
                <span className="truncate">{label}</span>
              </div>
            ))}
          </>
        )}
      </nav>

      {/* Footer */}
      <div
        className="px-3 pt-1 pb-3 space-y-[1px]"
        style={{ borderTop: "1px solid var(--border)" }}
      >
        <button
          className="w-full flex items-center gap-2.5 px-2 h-[30px] rounded-md text-[12.5px] transition-colors"
          style={{ color: "var(--ink-muted)" }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = "var(--bg-hover)";
            e.currentTarget.style.color = "var(--ink)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = "transparent";
            e.currentTarget.style.color = "var(--ink-muted)";
          }}
        >
          <Settings className="w-[14px] h-[14px]" strokeWidth={1.75} />
          <span>Settings</span>
        </button>

        <div className="pt-2 mt-1" style={{ borderTop: "1px solid var(--border)" }} />

        <div className="relative flex items-center gap-2 px-1 py-1.5" ref={menuRef}>
          <div
            className="w-6 h-6 rounded-full shrink-0 flex items-center justify-center text-[11px] font-semibold"
            style={{
              background:
                "linear-gradient(135deg, #ef4444 0%, #991b1b 60%, #450a0a 100%)",
              color: "#fff",
              boxShadow: "0 0 8px -2px rgba(239, 68, 68, 0.6)",
            }}
          >
            {displayName.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0 leading-tight">
            <div className="text-[12px] truncate font-medium" style={{ color: "var(--ink)" }}>
              {displayName}
            </div>
            {userEmail && (
              <div
                className="text-[10.5px] truncate"
                style={{ color: "var(--ink-soft)" }}
                title={userEmail}
              >
                {userEmail}
              </div>
            )}
          </div>
          <button
            onClick={() => setMenuOpen((v) => !v)}
            className="w-6 h-6 rounded-md flex items-center justify-center transition-colors"
            style={{ color: "var(--ink-soft)" }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "var(--bg-hover)";
              e.currentTarget.style.color = "var(--ink)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "transparent";
              e.currentTarget.style.color = "var(--ink-soft)";
            }}
            aria-label="Account menu"
          >
            <MoreHorizontal className="w-3.5 h-3.5" />
          </button>

          {menuOpen && (
            <div
              className="absolute bottom-full right-0 mb-1 w-44 rounded-md overflow-hidden z-20"
              style={{
                background: "var(--bg-elev)",
                border: "1px solid var(--border)",
                boxShadow: "0 14px 30px -8px rgba(0, 0, 0, 0.65)",
              }}
            >
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-2 px-2.5 h-8 text-[12px] transition-colors"
                style={{ color: "var(--ink-muted)" }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = "var(--bg-hover)";
                  e.currentTarget.style.color = "var(--securiva-red)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = "transparent";
                  e.currentTarget.style.color = "var(--ink-muted)";
                }}
              >
                <LogOut className="w-3.5 h-3.5" />
                Log out
              </button>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
