import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github-dark.css";
import "./ChatBox.css";
import ChatSidebar from "./ChatSidebar";
import { useTranslation } from "react-i18next";

function ChatBox() {
  const { t } = useTranslation();

  const [messages, setMessages] = useState([
    {
      role: "system",
      content: t("chatbox.system.default")
    }
  ]);

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(null);

  const conversationIdRef = useRef(null);
  const messagesContainerRef = useRef(null);

  useEffect(() => {
    const loadChat = async () => {
      try {
        const res = await fetch("http://localhost:8000/chat/latest", {
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
  }, []);

  useEffect(() => {
    const container = messagesContainerRef.current;
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim()) return;

    setError(null);

    const userMessage = { role: "user", content: input };
    const newMessages = [...messages, userMessage];

    setMessages(newMessages);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: newMessages,
          model: "gpt-3.5-turbo",
          api: "openai"
        })
      });

      if (!response.ok) {
        throw new Error(t("chatbox.errors.backendError") + `: ${response.status}`);
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

      const saveRes = await fetch("http://localhost:8000/chat/save", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          version: conversationId ?? undefined,
          messages: updatedMessages
        })
      });

      if (!saveRes.ok) {
        throw new Error(t("chatbox.errors.backendError"));
      }

      const saveData = await saveRes.json();

      conversationIdRef.current = saveData.version;
      setConversationId(saveData.version);

    } catch (err) {
      console.error("Chat error:", err);
      setError(err.message || t("chatbox.errors.failedResponse"));

      setMessages([
        ...newMessages,
        {
          role: "assistant",
          content: `❌ ${t("chatbox.messages.errorPrefix")}: ${
            err.message || t("chatbox.errors.failedResponse")
          }`
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setConversationId(null);
    setMessages([
      {
        role: "system",
        content: t("chatbox.system.newChat")
      }
    ]);
  };

  const handleSelectChat = async (version) => {
    try {
      const res = await fetch(
        `http://localhost:8000/chat/get?version=${version}`,
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
    <div className="flex h-screen w-screen bg-white text-black">
      <ChatSidebar
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
      />

      <div className="chat-layout">
        <div className="chatbox">

          <div className="chatbox-messages" ref={messagesContainerRef}>
            {messages
              .filter(msg => msg.role !== "system")
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

                    {isUser && (
                      <div className="avatar user-avatar">👤</div>
                    )}
                  </div>
                );
              })}

            {isLoading && (
              <div className="chat-row assistant">
                <div className="chat-bubble">
                  {t("chatbox.input.thinking")}
                </div>
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
              placeholder={t("chatbox.input.placeholder")}
              disabled={isLoading}
            />

            <button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
            >
              {t("chatbox.input.send")}
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}

export default ChatBox;