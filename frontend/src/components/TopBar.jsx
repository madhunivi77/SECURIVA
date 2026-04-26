import { useLocation } from "react-router-dom";
import { ChevronDown, MoreHorizontal } from "lucide-react";

const PAGE_META = {
  "/dashboard": { scope: "All Chats", title: "Overview" },
  "/dashboard/chat": { scope: "All Chats", title: "Chat" },
  "/dashboard/voice": { scope: "All Chats", title: "Voice" },
  "/dashboard/logs": { scope: "All Chats", title: "Activity" },
  "/dashboard/handbook": { scope: "All Chats", title: "AI Handbook" },
  "/dashboard/integrations": { scope: "All Chats", title: "Integrations" },
};

function metaFor(pathname) {
  if (PAGE_META[pathname]) return PAGE_META[pathname];
  const match = Object.keys(PAGE_META)
    .filter((p) => pathname === p || pathname.startsWith(p + "/"))
    .sort((a, b) => b.length - a.length)[0];
  return PAGE_META[match] || { scope: "All Chats", title: "" };
}

export default function TopBar() {
  const { pathname } = useLocation();
  const { scope, title } = metaFor(pathname);

  return (
    <header
      className="sticky top-0 z-10 h-12 px-4 flex items-center justify-between backdrop-blur-sm"
      style={{
        background: "rgba(10, 15, 31, 0.7)",
        borderBottom: "1px solid var(--border)",
      }}
    >
      <button
        className="flex items-center gap-1 px-2 h-7 rounded-md text-[12.5px] transition-colors"
        style={{ color: "var(--ink)" }}
        onMouseEnter={(e) => (e.currentTarget.style.background = "var(--bg-hover)")}
        onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
      >
        <span>{scope}</span>
        <ChevronDown
          className="w-3 h-3"
          strokeWidth={2.5}
          style={{ color: "var(--ink-soft)" }}
        />
      </button>

      {/* Page title — mono uppercase, Securiva public-site style */}
      <div
        className="absolute left-1/2 -translate-x-1/2 text-[11.5px] uppercase tracking-[0.28em]"
        style={{ color: "var(--ink)", fontWeight: 500 }}
      >
        {title}
      </div>

      <button
        className="w-7 h-7 rounded-md flex items-center justify-center transition-colors"
        style={{ color: "var(--ink-soft)" }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = "var(--bg-hover)";
          e.currentTarget.style.color = "var(--ink)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = "transparent";
          e.currentTarget.style.color = "var(--ink-soft)";
        }}
        aria-label="More"
      >
        <MoreHorizontal className="w-4 h-4" />
      </button>
    </header>
  );
}
