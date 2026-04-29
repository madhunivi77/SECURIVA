import { useState, useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github-dark.css";
import "./ChatBox.css";
import ChatSidebar from "./ChatSidebar";
import { useTranslation } from "react-i18next";

function ChatBox() {
  const { t } = useTranslation();

  const location = useLocation();
  const navigate = useNavigate();
  const initialMessage = location.state?.initialMessage;
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
    // Seed assistant placeholder we'll stream into
    const assistantSeed = { role: "assistant", content: "", toolStatus: null };
    const baseMessages = [...messages, userMessage];
    const streamingIndex = baseMessages.length; // index of the assistant placeholder

    setMessages([...baseMessages, assistantSeed]);
    setInput("");
    setIsLoading(true);

    // Helpers to mutate just the streaming assistant message
    const patchStreaming = (patch) => {
      setMessages((prev) => {
        const next = [...prev];
        if (next[streamingIndex]) {
          next[streamingIndex] = { ...next[streamingIndex], ...patch };
        }
        return next;
      });
    };
    const appendStreamingContent = (delta) => {
      setMessages((prev) => {
        const next = [...prev];
        if (next[streamingIndex]) {
          next[streamingIndex] = {
            ...next[streamingIndex],
            content: (next[streamingIndex].content || "") + delta,
            toolStatus: null, // tokens arriving — clear any tool badge
          };
        }
        return next;
      });
    };

    let finalContent = "";

    try {
      const response = await fetch("/api/chat/stream", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: baseMessages }),
      });

      if (!response.ok || !response.body) {
        throw new Error(t("chatbox.errors.backendError") + `: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        // SSE frames separated by blank lines
        let sep;
        while ((sep = buffer.indexOf("\n\n")) !== -1) {
          const frame = buffer.slice(0, sep);
          buffer = buffer.slice(sep + 2);
          if (!frame.startsWith("data: ")) continue;
          const payload = frame.slice(6).trim();
          if (payload === "[DONE]") break;

          let evt;
          try {
            evt = JSON.parse(payload);
          } catch {
            continue;
          }

          switch (evt.type) {
            case "token":
              finalContent += evt.content || "";
              appendStreamingContent(evt.content || "");
              break;
            case "tool_start":
              patchStreaming({ toolStatus: { name: evt.name, state: "running" } });
              break;
            case "tool_end":
              patchStreaming({
                toolStatus: {
                  name: evt.name,
                  state: evt.error ? "error" : "done",
                  durationMs: evt.duration_ms,
                },
              });
              break;
            case "blocked":
              finalContent = evt.response || "Request blocked.";
              patchStreaming({ content: finalContent, toolStatus: null });
              break;
            case "error":
              throw new Error(evt.error || "Stream error");
            case "done":
              // No-op; final content already streamed
              break;
          }
        }
      }

      // Persist the conversation
      const updatedMessages = [
        ...baseMessages,
        { role: "assistant", content: finalContent },
      ];
      const saveRes = await fetch("/chat/save", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          version: conversationId ?? undefined,
          messages: updatedMessages,
        }),
      });
      if (saveRes.ok) {
        const saveData = await saveRes.json();
        conversationIdRef.current = saveData.version;
        setConversationId(saveData.version);
      }
    } catch (err) {
      console.error("Chat error:", err);
      setError(err.message || t("chatbox.errors.backendError"));
      patchStreaming({
        content: `❌ ${t("chatbox.messages.errorPrefix")}: ${err.message || t("chatbox.errors.failedResponse")}`,
        toolStatus: null,
      });
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
        content: t("chatbox.system.newChat")
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
    <div className="flex h-full w-full" style={{ color: "var(--ink)" }}>
      <div className="chat-layout">
        <ChatSidebar
          onNewChat={handleNewChat}
          onSelectChat={handleSelectChat}
        />
        <div className="chatbox">
          <div className="chatbox-messages" ref={messagesContainerRef}>
            {messages
              .filter((msg) => msg.role !== "system")
              .map((msg, index) => {
                const isUser = msg.role === "user";
                const isEmptyAssistant = !isUser && !msg.content;
                return (
                  <div
                    key={index}
                    className={`chat-row ${isUser ? "user" : "assistant"}`}
                  >
                    {!isUser && (
                      <div className="avatar agent-avatar">
                        <img src="/BlueLogoNoText.png" alt="Securiva" />
                      </div>
                    )}
                    <div className="chat-bubble">
                      {!isUser && msg.toolStatus && (
                        <div className="tool-status">
                          <span
                            className={`tool-status-dot ${
                              msg.toolStatus.state === "error"
                                ? "error"
                                : msg.toolStatus.state === "done"
                                ? "done"
                                : "running"
                            }`}
                          />
                          <span className="tool-status-label">
                            {msg.toolStatus.state === "running"
                              ? `Calling ${msg.toolStatus.name}…`
                              : msg.toolStatus.state === "done"
                              ? `${msg.toolStatus.name} ·\u00A0${Math.round(msg.toolStatus.durationMs || 0)}ms`
                              : `${msg.toolStatus.name} failed`}
                          </span>
                        </div>
                      )}
                      {isEmptyAssistant && !msg.toolStatus ? (
                        <span className="stream-dots">
                          <span />
                          <span />
                          <span />
                        </span>
                      ) : (
                        <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
                          {msg.content}
                        </ReactMarkdown>
                      )}
                    </div>
                    {isUser && <div className="avatar user-avatar">U</div>}
                  </div>
                );
              })}
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