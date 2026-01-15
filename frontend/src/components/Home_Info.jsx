import React from "react";
import Card from "./Card";

export default function Home_Info() {
  return (
    <div className="info">
      <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: "50px",
            //maxWidth: "1100px",
            margin: "0 auto",
            padding: "80px",
            color: "black",
          }}
        >
          <Card image={"/AI_Virtual_assistant.png"} title={"AI Virtual Agent"} text={"Streamline workflows, scheduling, and communications with smart automation tools."}/>
          <Card image={"/Cybersecurity_Protection.png"} title={"Cybersecurity Protection"} text={"Real-time AI defense for data, users, and digital assets."}/>
          <Card image={"/AI_VPN.png"} title={"AI VPN"} text={"Secure every connection using adaptive, encrypted networking."}/>
          <Card image={"/Customer_Interaction.png"} title={"Customer Interaction"} text={"Manage calls, chats, and emails through an intelligent AI avatar."}/>
          <Card image={"/ebook.png"} title={"eBook Generator"} text={"Instantly create training manuals and awareness guides."}/>
          <Card image={"/Integrations.png"} title={"Integrations"} text={"Connect with Gmail, Microsoft 365, Salesforce, OpenAI, and more."}/>
        </div>
        
        <h2
          style={{
            fontSize: "40px",
            paddingTop: "30px",
          }}
        >
          💼 Why Choose SecuriVA
        </h2>
        <ul>
          <li>
            <strong>All-in-One Platform:</strong> AI automation, cybersecurity, and
            communication in one unified system.
          </li>
          <li>
            <strong>Enterprise-Grade Security:</strong> Built for complete protection
            with encrypted AI-driven systems.
          </li>
          <li>
            <strong>Intelligent & Human-Like:</strong> Engage with a smart,
            conversational AI assistant that adapts to your business.
          </li>
          <li>
            <strong>Seamless Integration:</strong> Works effortlessly with your
            existing tools and cloud services.
          </li>
          <li>
            <strong>Future-Ready:</strong> Powered by AI VPN and Digital Twin
            technology for next-generation innovation.
          </li>
        </ul>
    </div>
  );
}
