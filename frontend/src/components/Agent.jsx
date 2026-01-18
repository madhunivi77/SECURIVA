import React from "react";
import Card from "./Card";
import "./Agent.css";
import CenteredArrow from "./CenteredArrow";

function Agent() {
    return (
        <div>
            <header className="hero">
                <div className="hero-content" style={{ display: "flex", justifyContent: "space-evenly" }}>
                    <div>
                        <h1 style={{ fontSize: 40, textAlign: "left", paddingTop: "20px" }}>INTELLIGENT AI AGENT FOR CUSTOMIZED WORKFLOWS</h1>
                        <p style={{ fontSize: 25, textAlign: "left", paddingTop: "30px", paddingBottom: "40px" }}>
                            SecuriVA's integrated AI agent allows you to effortlessly construct automated workflows and generate security insights.
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
                            src="/agent.png"
                            alt="agent_page_image"
                            style={{
                                height: "auto",
                                width: "650px",
                                //objectFit: "cover",
                                //borderRadius: "6px",
                                paddingTop: "30px",
                                paddingLeft: "30px",
                                paddingBottom: "30px",
                            }}
                        />
                    </div>
                </div>
            </header>

            <h1 style={{ textAlign: "center" }}>Meet AVA, SecuriVA's Intelligent AI Agent</h1>

            <div className="graph" style={{ color: "black" }}>

                <div className="layer">
                    <Card image={"/agent_page/AVA_Assistant.png"} title={"AVA"} text={"SecuriVA AI Bot"} />
                </div>

                <CenteredArrow />

                <div className="layer">
                    <Card image={"/agent_page/email.png"} title={"Email"} text={"Send and Respond"} />
                    <Card image={"/agent_page/whatsapp.png"} title={"WhatsApp"} text={"Auto-replies"} />
                    <Card image={"/agent_page/sms.png"} title={"SMS Texting"} text={"Automated Alerts"} />
                </div>
                
                <div style={{display: "flex", flexDirection: "row", justifyContent: "center", gap: "30%"}}>
                    <CenteredArrow />
                    <CenteredArrow />
                    <CenteredArrow />
                </div>

                <div className="layer">
                    <Card image={"/agent_page/call.png"} title={"Calls"} text={"Voice Assistant"} />
                    <Card image={"/agent_page/calendar.png"} title={"Calendar"} text={"Meetings & Bookings"} />
                    <Card image={"/agent_page/shield.png"} title={"Cyber Shield"} text={"Secure Workflows"} />
                </div>

                <CenteredArrow />

                <div className="layer">
                    <Card image={"/agent_page/integration.png"} title={"Integration Hub"} text={"Gmail • WhatsApp API • WordPress • Shopify • Salesforce • AWS • SMS"} />
                </div>

                <CenteredArrow />

                <div className="layer">
                    <Card image={"/agent_page/automation.png"} title={"SecuriVA Automation Engine"} text={"Emails • Calls • Tasks • Alerts • AI Responses • Scheduling"} />
                </div>
            </div>
        </div>
    )
}

export default Agent;