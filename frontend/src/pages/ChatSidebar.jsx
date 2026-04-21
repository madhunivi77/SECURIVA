import { useState, useEffect } from "react";
import { MessageSquarePlus, Trash2, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";

function ChatSidebar({ onNewChat, onSelectChat }) {
  const [conversations, setConversations] = useState([]);
  const navigate = useNavigate();

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

  useEffect(() => {
    loadConversations();
  }, []);

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

  return (
    <aside className="w-64 shrink-0 bg-white border-r border-zinc-200 flex flex-col">
      <div className="h-14 px-4 flex items-center gap-2.5 border-b border-zinc-200">
        <button
          onClick={() => navigate("/dashboard")}
          className="w-7 h-7 rounded-md flex items-center justify-center text-zinc-500 hover:bg-zinc-100 hover:text-zinc-900 transition-colors"
          aria-label="Back"
        >
          <ArrowLeft size={16} />
        </button>
        <span className="text-sm font-semibold tracking-tight text-zinc-900">
          Chats
        </span>
      </div>

      <div className="p-3">
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 bg-zinc-900 text-white text-sm font-medium py-2 rounded-md hover:bg-zinc-800 transition-colors"
        >
          <MessageSquarePlus size={16} />
          New chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-2 pb-2">
        {conversations.length === 0 ? (
          <div className="text-xs text-zinc-500 px-3 py-2">
            No previous chats yet
          </div>
        ) : (
          <div className="space-y-0.5">
            {conversations.map((chat) => (
              <div
                key={chat.version}
                onClick={() => onSelectChat(chat.version)}
                className="group px-2.5 py-2 rounded-md cursor-pointer text-sm flex justify-between items-center gap-2 text-zinc-700 hover:bg-zinc-100 hover:text-zinc-900 transition-colors"
              >
                <span className="truncate flex-1">{chat.title}</span>
                <Trash2
                  size={14}
                  className="text-zinc-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition shrink-0"
                  onClick={(e) => handleDelete(chat.version, e)}
                />
              </div>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}

export default ChatSidebar;
