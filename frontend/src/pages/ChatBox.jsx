import { useState, useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github.css";
import "./ChatBox.css";
import ChatSidebar from "./ChatSidebar";

function ChatBox() {
  const location = useLocation();
  const navigate = useNavigate();
  const initialMessage = location.state?.initialMessage;
  const [messages, setMessages] = useState([
    {
      role: "system",
      content:
        "You are a helpful assistant. You have access to tools. Respond in markdown."
    }
  ]);

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const conversationIdRef = useRef(null);

  const messagesContainerRef = useRef(null);

 
  useEffect(() => {
    // If we arrived with an initialMessage, skip loading prior history —
    // the user wants a new conversation with that prompt.
    if (initialMessage) return;

    const loadChat = async () => {
      try {
        const res = await fetch("/chat/latest", {
          credentials: "include"
        });

        if (!res.ok) return;

        const data = await res.json();

        if (Array.isArray(data.messages)) {
          setMessages(data.messages);
          setConversationId(data.version);
          conversationIdRef.current = data.version;
        }
      } catch (err) {
        console.error("Failed to load chat history", err);
      }
    };

    loadChat();
  }, [initialMessage]);

 
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }, [messages, isLoading]);

  
  const handleSend = async (overrideText) => {
    const text = (overrideText ?? input).trim();
    if (!text) return;

    setError(null);

    const userMessage = { role: "user", content: text };
    const newMessages = [...messages, userMessage];

    setMessages(newMessages);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          messages: newMessages
        })
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`);
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      const assistantMessage = {
        role: "assistant",
        content: data.response
      };

      const updatedMessages = [...newMessages, assistantMessage];
      setMessages(updatedMessages);
      console.log("Saving with version:", conversationId);
      
      
      const saveRes = await fetch("/chat/save", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          version: conversationId ?? undefined, 
          messages: updatedMessages
        })
      });

      if (!saveRes.ok) {
        throw new Error("Failed to save chat");
      }

      const saveData = await saveRes.json();

      conversationIdRef.current = saveData.version;
      setConversationId(saveData.version);
    } catch (err) {
      console.error("Chat error:", err);
      setError(err.message || "Failed to get response");

      setMessages([
        ...newMessages,
        {
          role: "assistant",
          content: `❌ Error: ${err.message || "Failed to get response"}`
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };
  // One-shot: if we arrived with an initialMessage from the Home page,
  // fire it as the first user turn and then clear the location state so a
  // refresh doesn't re-send it.
  const initialSentRef = useRef(false);
  useEffect(() => {
    if (!initialMessage || initialSentRef.current) return;
    initialSentRef.current = true;
    handleSend(initialMessage);
    navigate(location.pathname, { replace: true, state: {} });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialMessage]);

  const handleNewChat = () => {
    setConversationId(null);   
    setMessages([
      {
        role: "system",
        content: "You are a helpful assistant."
      }
    ]);
  };

  
  
  const handleSelectChat = async (version) => {
    try {
      const res = await fetch(
        `/chat/get?version=${version}`,
        { credentials: "include" }
      );
  
      if (!res.ok) return;
  
      const data = await res.json();
  
      setMessages(data.messages);
      setConversationId(version);
    } catch (err) {
      console.error("Failed to load chat", err);
    }
  };
  return (
    <div className="flex h-full w-full bg-white text-zinc-900">
      <ChatSidebar
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
      />

      <div className="chat-layout">
        <div className="chatbox">
          <div className="chatbox-messages" ref={messagesContainerRef}>
            {messages
              .filter((msg) => msg.role !== "system")
              .map((msg, index) => {
                const isUser = msg.role === "user";
                return (
                  <div
                    key={index}
                    className={`chat-row ${isUser ? "user" : "assistant"}`}
                  >
                    {!isUser && (
                      <div className="avatar agent-avatar">
                        <img src="/logo.png" alt="Agent" />
                      </div>
                    )}
                    <div className="chat-bubble">
                      <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                    {isUser && <div className="avatar user-avatar">U</div>}
                  </div>
                );
              })}

            {isLoading && (
              <div className="chat-row assistant">
                <div className="avatar agent-avatar">
                  <img src="/logo.png" alt="Agent" />
                </div>
                <div className="chat-bubble">Thinking…</div>
              </div>
            )}
          </div>

          <div className="chatbox-input">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) =>
                e.key === "Enter" && !isLoading && handleSend()
              }
              placeholder="Type a message..."
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChatBox;