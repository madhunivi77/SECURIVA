import React from "react";

function Card({ image, title, text }) {
  return (
    <div
      style={{
        background: "#f7f7f7",
        padding: "20px",
        borderRadius: "16px",
        boxShadow: "0 4px 10px rgba(0,0,0,0.08)",
        border: "1px solid #e5e5e5",
        textAlign: "center",
      }}
    >
      <img
        src={image}
        alt={title}
        style={{ width: "100%", height: "auto" }}
      />

      <h3 style={{ width: "100%", marginBottom: "10px", fontSize: "25px" }}>
        {title}
      </h3>

      <p style={{ width: "100%", fontSize: "15px", lineHeight: "1.5" }}>
        {text}
      </p>
    </div>
  );
}

export default Card;