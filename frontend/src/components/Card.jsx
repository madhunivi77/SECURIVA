import React from "react";

function Card({image, title, text}){
    return (
        <div
              style={{
                background: "#f7f7f7",
                padding: "20px",
                borderRadius: "16px",
                textAlign: "center",
                boxShadow: "0 4px 10px rgba(0,0,0,0.08)",
                border: "1px solid #e5e5e5",
                flexDirection: "column",
                justifyContent: "flex-start",
              }}
            >
              <img src={image} alt={title} style={{ width: "100%", height: "auto" }} className="mx-auto mb-4" />
              <h3 style={{ marginBottom: "10px", fontSize: "25px", textAlign: "center" }}>
                {title}
              </h3>
              <p style={{ fontSize: "15px", lineHeight: "1.5" }}>{text}</p>
            </div>
    );
}

export default Card;