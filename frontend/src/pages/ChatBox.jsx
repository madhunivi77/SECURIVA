import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github-dark.css";
import "./ChatBox.css";



function ChatBox() {
  const [messages, setMessages] = useState([
    {
      role: "system",
      content:
        "You are a helpful assistant. You have access to a set of tools. Only use these tools when the user asks you to perform a specific action that requires them. Output your response in markdown format so that it can be rendered properly in a markdown viewer."
    }
  ]);

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const messagesContainerRef = useRef(null);



// LOAD CHAT HISTORY (BACKEND)

  useEffect(() => {
    const loadChatHistory = async () => {
      try {
        const res = await fetch(
          "http://localhost:8000/chat/latest",
          {
            credentials: "include" 
          }
        );

        if (!res.ok) return;

        const data = await res.json();

        if (Array.isArray(data.messages)) {
          setMessages(data.messages);
        }
      } catch (err) {
        console.error("Failed to load chat history", err);
      }
    };

    loadChatHistory();
  }, []);

  /* Auto-scroll */
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }, [messages, isLoading]);

  /* ---------------------------------
     SEND MESSAGE
  ---------------------------------- */
  const handleSend = async () => {
    if (!input.trim()) return;

    setError(null);

    const userMessage = { role: "user", content: input };
    const newMessages = [...messages, userMessage];

    setMessages(newMessages);
    setInput("");
    setIsLoading(true);

    try {
      /* Existing LLM call (unchanged except auth added) */
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        credentials: "include", // send api_key cookie
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          messages: newMessages,
          model: "gpt-3.5-turbo",
          api: "openai"
        })
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`);
      }

      const data = await response.json();

      const assistantMessage = {
        role: "assistant",
        content: data.response
      };

      const updatedMessages = [...newMessages, assistantMessage];
      setMessages(updatedMessages);

      /* Save chat history */
      await fetch("http://localhost:8000/chat/save", {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json"},
          body: JSON.stringify(updatedMessages)
            });
      

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

  /* ---------------------------------
     CLEAR CHAT (BACKEND)
  ---------------------------------- */
  const handleClearChat = async () => {
    try {
      await fetch(
        `http://localhost:8000/chat/delete`,
        {
          method: "DELETE",
          credentials : "include"
        }
      );
    } catch (err) {
      console.error("Failed to delete chat:", err);
    }

    setMessages([
      {
        role: "system",
        content:
          "You are a helpful assistant. You have access to a set of tools."
      },
      {
        role: "assistant",
        content: "Chat cleared! How can I help you?"
      }
    ]);

    setError(null);
  };

  return (
    <div className="chatbox">
      <div className="chatbox-header">
        <button onClick={handleClearChat}>Clear Chat</button>
        <span>AI Chat (OpenAI + MCP Tools)</span>
      </div>

      {error && (
        <div style={{ padding: "10px", backgroundColor: "#fee", color: "#c00" }}>
          Error: {error}
        </div>
      )}

      <div className="chatbox-messages" ref={messagesContainerRef}>
        {messages
          .filter(msg => msg.role !== "system")
          .map((msg, index) => (
            <div
              key={index}
              className={`chatbox-message ${
                msg.role === "user" ? "user" : "bot"
              }`}
            >
              <strong>
                {msg.role === "user" ? "You" : "Assistant"}:
              </strong>
              <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
                {msg.content}
              </ReactMarkdown>
            </div>
          ))}
        {isLoading && (
          <div className="chatbox-message bot">
            <strong>Assistant:</strong> <em>Thinking...</em>
          </div>
        )}
      </div>

      <div className="chatbox-input">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleSend()}
          placeholder="Type a message..."
          disabled={isLoading}
        />
        <button onClick={handleSend} disabled={isLoading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatBox;
