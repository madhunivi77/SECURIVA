import { useEffect, useRef, useState } from "react";
import {
  Menu,
  X,
  MessageSquarePlus,
  Trash2,
  MessageSquare,
} from "lucide-react";

/**
 * Chat menu — anchor button top-right, popover opens beneath it.
 * Click outside or ESC to dismiss.
 */
export default function ChatSidebar({ onNewChat, onSelectChat }) {
  const [conversations, setConversations] = useState([]);
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);

  const loadConversations = async () => {
    try {
      const res = await fetch("/chat/list", { credentials: "include" });
      if (!res.ok) return;
      const data = await res.json();
      setConversations(data.conversations || []);
    } catch (err) {
      console.error("Failed to load conversations", err);
    }
  };

  // Load on first open + whenever reopened (so new chats show up)
  useEffect(() => {
    if (open) loadConversations();
  }, [open]);

  // ESC closes · click outside closes
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => {
      if (e.key === "Escape") setOpen(false);
    };
    const onClick = (e) => {
      if (rootRef.current && !rootRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    window.addEventListener("keydown", onKey);
    document.addEventListener("mousedown", onClick);
    return () => {
      window.removeEventListener("keydown", onKey);
      document.removeEventListener("mousedown", onClick);
    };
  }, [open]);

  const handleDelete = async (version, e) => {
    e.stopPropagation();
    try {
      await fetch(`/chat/delete_by_version?version=${version}`, {
        method: "DELETE",
        credentials: "include",
      });
      setConversations((prev) =>
        prev.filter((chat) => chat.version !== version)
      );
    } catch (err) {
      console.error("Failed to delete chat", err);
    }
  };

  const pickAndClose = (version) => {
    onSelectChat(version);
    setOpen(false);
  };

  const newAndClose = () => {
    onNewChat();
    setOpen(false);
  };

  return (
    <div
      ref={rootRef}
      className="absolute top-3 right-4 z-30"
      style={{ fontFamily: "var(--font-mono)" }}
    >
      {/* Toggle */}
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1.5 h-8 pl-2.5 pr-2 rounded-md text-[12px] transition-colors"
        style={{
          background: open ? "var(--bg-elev)" : "rgba(255,255,255,0.02)",
          border: `1px solid ${open ? "var(--ink-muted)" : "var(--border)"}`,
          color: open ? "var(--ink)" : "var(--ink-muted)",
        }}
        onMouseEnter={(e) => {
          if (!open) {
            e.currentTarget.style.color = "var(--ink)";
            e.currentTarget.style.borderColor = "var(--ink-muted)";
          }
        }}
        onMouseLeave={(e) => {
          if (!open) {
            e.currentTarget.style.color = "var(--ink-muted)";
            e.currentTarget.style.borderColor = "var(--border)";
          }
        }}
        aria-expanded={open}
        aria-label="Chat history"
      >
        <Menu className="w-3.5 h-3.5" strokeWidth={2} />
        <span>Chats</span>
        {conversations.length > 0 && (
          <span
            className="text-[10px] px-1 ml-0.5 rounded tabular-nums"
            style={{
              background: "var(--border)",
              color: "var(--ink-muted)",
            }}
          >
            {conversations.length}
          </span>
        )}
      </button>

      {/* Popover panel */}
      {open && (
        <div
          className="absolute top-[40px] right-0 w-[300px] rounded-md flex flex-col overflow-hidden"
          style={{
            background: "var(--bg-elev)",
            border: "1px solid var(--border)",
            boxShadow:
              "0 0 0 1px rgba(239, 68, 68, 0.05), 0 20px 44px -10px rgba(0,0,0,0.75)",
            maxHeight: "calc(100vh - 140px)",
            animation: "chat-menu-in 180ms cubic-bezier(0.16, 1, 0.3, 1)",
          }}
        >
          {/* Header */}
          <div
            className="px-3 h-10 flex items-center justify-between shrink-0"
            style={{ borderBottom: "1px solid var(--border)" }}
          >
            <span
              className="text-[10.5px] uppercase tracking-[0.22em]"
              style={{ color: "var(--ink-muted)", fontWeight: 500 }}
            >
              Chat history
            </span>
            <button
              onClick={() => setOpen(false)}
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
              aria-label="Close"
            >
              <X className="w-3.5 h-3.5" strokeWidth={2} />
            </button>
          </div>

          {/* New chat CTA */}
          <div className="p-2 shrink-0">
            <button
              onClick={newAndClose}
              className="sv-cta w-full justify-center"
            >
              <MessageSquarePlus className="w-3.5 h-3.5" />
              New chat
            </button>
          </div>

          {/* List */}
          <div
            className="flex-1 overflow-y-auto px-2 pb-2 space-y-[1px]"
            style={{ borderTop: "1px solid var(--border)" }}
          >
            {conversations.length === 0 ? (
              <div
                className="flex flex-col items-center text-center py-6 px-3 gap-2"
                style={{ color: "var(--ink-soft)" }}
              >
                <div
                  className="w-8 h-8 rounded-md flex items-center justify-center"
                  style={{
                    background: "var(--bg-deep)",
                    border: "1px solid var(--border)",
                  }}
                >
                  <MessageSquare
                    className="w-4 h-4"
                    strokeWidth={1.75}
                    style={{ color: "var(--ink-muted)" }}
                  />
                </div>
                <div
                  className="text-[11px] uppercase tracking-[0.2em]"
                  style={{ color: "var(--ink-muted)", fontWeight: 500 }}
                >
                  No history
                </div>
                <p
                  className="text-[11px] leading-relaxed max-w-[200px]"
                  style={{ color: "var(--ink-soft)" }}
                >
                  Your saved chats will appear here.
                </p>
              </div>
            ) : (
              <div className="pt-2">
                {conversations.map((chat) => (
                  <div
                    key={chat.version}
                    onClick={() => pickAndClose(chat.version)}
                    className="group px-2 h-[32px] rounded-md cursor-pointer text-[12px] flex justify-between items-center gap-2 transition-colors"
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
                    <span className="truncate flex-1">{chat.title}</span>
                    <button
                      className="opacity-0 group-hover:opacity-100 transition shrink-0 w-5 h-5 rounded flex items-center justify-center"
                      style={{ color: "var(--ink-soft)" }}
                      onMouseEnter={(e) =>
                        (e.currentTarget.style.color = "var(--securiva-red)")
                      }
                      onMouseLeave={(e) =>
                        (e.currentTarget.style.color = "var(--ink-soft)")
                      }
                      onClick={(e) => handleDelete(chat.version, e)}
                      aria-label="Delete chat"
                    >
                      <Trash2 size={12} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          {conversations.length > 0 && (
            <div
              className="px-3 h-8 flex items-center justify-between text-[10px] uppercase tracking-[0.2em] shrink-0"
              style={{
                borderTop: "1px solid var(--border)",
                color: "var(--ink-soft)",
                background: "rgba(5, 9, 26, 0.5)",
              }}
            >
              <span>
                {conversations.length}{" "}
                {conversations.length === 1 ? "entry" : "entries"}
              </span>
              <span style={{ color: "var(--ink-dim)" }}>esc · close</span>
            </div>
          )}
        </div>
      )}

      <style>{`
        @keyframes chat-menu-in {
          from { opacity: 0; transform: translateY(-8px) scale(0.98); }
          to { opacity: 1; transform: translateY(0) scale(1); }
        }
      `}</style>
    </div>
  );
}
