import React from "react";
import Card from "./Card";
function Security() {
    return (
        <div>
            {/* ---------- HEADER ---------- */}
            <header className="hero">
                <div className="hero-content" style={{display: "flex", justifyContent: "space-evenly"}}>
                    <div>
                        <h1 style={{fontSize: 40, textAlign: "left", paddingTop: "20px"}}>PROACTIVE SECURITY MEASURES TO PROTECT YOUR BUSINESS</h1>
                        <p style={{fontSize: 25, textAlign: "left", paddingTop: "30px", paddingBottom: "40px"}}>
                        SecuriVA's cyber defense core secures your business operations by providing a suite of real time monitoring appliances to give you peace of mind in a world of evolving cyber threats.
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
                        src="/Security_shield.png"
                        alt="security_page_image"
                        style={{
                            height: "auto",
                            width: "450px",
                            //objectFit: "cover",
                            //borderRadius: "6px",
                            paddingTop: "30px",
                            paddingLeft: "30px",
                        }}
                        />
                    </div>
                </div>
            </header>
            <h1 style={{textAlign: "center"}}>Protection Layers</h1>
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
                <Card image={""} title={"Domain Shield"} text={"Protect Domain"}/>
                <Card image={""} title={"SSL Encryption"} text={"Secure Connections"}/>
                <Card image={""} title={"AI Firewall"} text={"Block Threats"}/>
                <Card image={""} title={"VPN Secure"} text={"Encrypted Access"}/>
                <Card image={""} title={"Malware Scan"} text={"Detect Infections"}/>
                <Card image={""} title={"Cloud Backup"} text={"Auto Recovery"}/>
                <Card image={""} title={"Threat Intel"} text={"Predict Attacks"}/>
                <Card image={""} title={"Whois Privacy"} text={"Hide Identity"}/>
                <Card image={""} title={"Alerts & Logs"} text={"Real-time Warnings"}/>
            </div>
            <h1 style={{textAlign: "center"}}><span style={{color: "lightblue", fontSize: ".75em"}}>▼</span> ALL CONNECTED TO  <span style={{color: "lightblue", fontSize: ".75em"}}>▼</span></h1>
            <div style={{
                justifyContent: "center",
                color: "black"
            }}>
                <Card image={""} title={"SECURIVA AI ENGINE"} text={"Real-time monitoring & Automation Predict • Block • Secure • Recover"}/>
            </div>
        </div>
        
    )
}

export default Security;