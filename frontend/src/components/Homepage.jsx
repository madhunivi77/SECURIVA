// Homepage.jsx
import React from "react";
import Home_Info from "./Home_Info";

export default function Homepage({ onLoginClick }) {

  return (
    <div className="homepage">

      {/* ---------- HEADER ---------- */}
      <header className="hero">

        <div className="hero-content" style={{display: "flex", justifyContent: "space-evenly"}}>
          <div>
            <h1 style={{fontSize: 40, textAlign: "left", paddingTop: "20px"}}>THE AI PLATFORM THAT PROTECTS AND AUTOMATES YOUR BUSINESS</h1>
            <p style={{fontSize: 25, textAlign: "left", paddingTop: "30px", paddingBottom: "40px"}}>
              SecuriVA unifies AI automation, cybersecurity protection, and secure communication
              into one intelligent platform designed for modern enterprises.
            </p>
            <button
              style={{
                fontSize: 20,
                width: "200px",
                height: "70px",
                background: "red",
              }}
            >
              Start Free Trial
            </button>
          </div>

          <div style={{}}>
            <img
              src="/IMAGE_1.png"
              alt="homepage_image"
              style={{
                height: "auto",
                width: "600px",
                //objectFit: "cover",
                //borderRadius: "6px",
                paddingTop: "30px",
                paddingLeft: "30px",
              }}
            />
          </div>
        </div>
      </header>
      
      
    </div>
  );
}
