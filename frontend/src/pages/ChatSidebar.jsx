import { useState, useEffect } from "react";
import { MessageSquarePlus, Trash2 , ArrowLeft} from "lucide-react";
import { useNavigate } from "react-router-dom";

function ChatSidebar({ onNewChat, onSelectChat }) {
  const [conversations, setConversations] = useState([]);
  const navigate = useNavigate();

  
  const loadConversations = async () => {
    try {
      const res = await fetch("http://localhost:8000/chat/list", {
        credentials: "include"
      });

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
      await fetch(
        `http://localhost:8000/chat/delete_by_version?version=${version}`,
        {
          method: "DELETE",
          credentials: "include"
        }
      );

      
      setConversations(prev =>
        prev.filter(chat => chat.version !== version)
      );

    } catch (err) {
      console.error("Failed to delete chat", err);
    }
  };

  return (
    <aside className="w-64 bg-gray-900 text-white flex flex-col">
      <div className="p-4 text-xl font-semibold border-b border-gray-700 flex items-center gap-3">
        <ArrowLeft
          size={20}
          className="cursor-pointer hover:text-blue-400 transition"
          onClick={() => navigate("/dashboard")}
        />
        <span>Chat</span>
      </div>

      {/* new chat button */}
      <button
        onClick={onNewChat}
        className="m-3 w-[85%] mx-auto flex items-center justify-center gap-2 bg-white text-black font-medium p-3 rounded-lg"
      >
        <MessageSquarePlus size={18} />
        New Chat
      </button>

      {/* conversation list */}
      <div className="flex-1 overflow-y-auto px-3">
        {conversations.length === 0 ? (
          <div className="text-sm text-gray-400 mt-4">
            No previous chats yet
          </div>
        ) : (
          conversations.map((chat) => (
            <div
              key={chat.version}
              onClick={() => onSelectChat(chat.version)}
              className="mt-3 p-3 bg-gray-800 hover:bg-gray-700 rounded-lg cursor-pointer text-sm flex justify-between items-center group"
            >
              <span>{chat.title}</span>

              {/* Trash Icon */}
              <Trash2
                size={16}
                className="text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition cursor-pointer"
                onClick={(e) => handleDelete(chat.version, e)}
              />
            </div>
          ))
        )}
      </div>
    </aside>
  );
}

export default ChatSidebar;