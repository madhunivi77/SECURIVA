import { useState, useEffect, useRef } from "react";
import "./ChatBox.css";

function ChatBox({ authToken, csrfToken }) {
  // Initialize with system message in OpenAI format
  const [messages, setMessages] = useState(() => {
    const saved = localStorage.getItem("chat_messages");
    if (saved) {
      return JSON.parse(saved);
    }
    return [
      {
        role: "system",
        content: "You are a helpful assistant. You have access to a set of tools. Only use these tools when the user asks you to perform a specific action that requires them."
      }
    ];
  });

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Ref for auto-scrolling to bottom
  const messagesEndRef = useRef(null);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem("chat_messages", JSON.stringify(messages));
  }, [messages]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim()) return;

    // Clear any previous errors
    setError(null);

    // Add user message to context
    const userMessage = { role: "user", content: input };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput("");
    setIsLoading(true);

    try {
      // Log request details
      console.log("=== CHAT REQUEST DEBUG ===");
      console.log("CSRF Token:", csrfToken);
      console.log("Auth Token:", authToken);
      console.log("Credentials mode:", "include");
      console.log("All cookies:", document.cookie);

      // Call backend API
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": csrfToken, // Include CSRF token for protection
        },
        credentials: "include", // Include cookies
        body: JSON.stringify({
          messages: newMessages,
          model: "gpt-3.5-turbo", // Could make this configurable
          api: "openai" // Could make this configurable
        }),
      });

      console.log("Response status:", response.status);
      console.log("Response headers:", Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`);
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      // Add assistant response to context
      const assistantMessage = {
        role: "assistant",
        content: data.response
      };

      setMessages([...newMessages, assistantMessage]);

      // Log tool calls if any (for debugging)
      if (data.tool_calls && data.tool_calls.length > 0) {
        console.log("Tool calls made:", data.tool_calls);
      }

    } catch (err) {
      console.error("Chat error:", err);
      setError(err.message || "Failed to get response from backend");

      // Add error message to chat
      setMessages([
        ...newMessages,
        {
          role: "assistant",
          content: `❌ Error: ${err.message || "Failed to get response"}. Please try again.`
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    const initialMessages = [
      {
        role: "system",
        content: "You are a helpful assistant. You have access to a set of tools. Only use these tools when the user asks you to perform a specific action that requires them."
      },
      {
        role: "assistant",
        content: "Chat cleared! How can I help you?"
      }
    ];
    setMessages(initialMessages);
    setError(null);
  };

  return (
    <div className="chatbox">
      <div className="chatbox-header" style={{ padding: "10px", borderBottom: "1px solid #ccc" }}>
        <button onClick={handleClearChat} style={{ float: "right" }}>
          Clear Chat
        </button>
        <span>AI Chat (OpenAI + MCP Tools)</span>
      </div>

      {error && (
        <div style={{ padding: "10px", backgroundColor: "#fee", color: "#c00" }}>
          Error: {error}
        </div>
      )}

      <div className="chatbox-messages">
        {messages.filter(msg => msg.role !== "system").map((msg, index) => (
          <div
            key={index}
            className={`chatbox-message ${msg.role === "user" ? "user" : "bot"}`}
          >
            <strong>{msg.role === "user" ? "You" : "Assistant"}:</strong> {msg.content}
          </div>
        ))}
        {isLoading && (
          <div className="chatbox-message bot">
            <strong>Assistant:</strong> <em>Thinking...</em>
          </div>
        )}
        {/* Invisible div at the bottom for auto-scroll */}
        <div ref={messagesEndRef} />
      </div>

      <div className="chatbox-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !isLoading && handleSend()}
          placeholder={isLoading ? "Waiting for response..." : "Type a message..."}
          disabled={isLoading}
        />
        <button onClick={handleSend} disabled={isLoading || !input.trim()}>
          {isLoading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}

export default ChatBox;