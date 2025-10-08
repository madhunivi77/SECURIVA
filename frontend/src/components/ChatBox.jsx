import { useState } from "react";
import "./ChatBox.css";

function ChatBox() {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hi! I am a chatbox." }
  ]);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { sender: "user", text: input }];

    let botReply = "I can't understand anything other than hello. :(";
    if (input.toLowerCase() === "hello") {
      botReply = "Hello!";
    }

    newMessages.push({ sender: "bot", text: botReply });

    setMessages(newMessages);
    setInput("");
  };

  return (
    <div className="chatbox">
      <div className="chatbox-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`chatbox-message ${msg.sender}`}>
            <strong>{msg.sender === "user" ? "You" : "Bot"}:</strong> {msg.text}
          </div>
        ))}
      </div>
      <div className="chatbox-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Type a message..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}

export default ChatBox;