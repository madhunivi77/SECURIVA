import Card from "./Card";
import "./Agent.css";
import CenteredArrow from "./CenteredArrow";

function Agent() {
    return (
        <div>
            <header className="hero section-min-height">
                <div className="hero-content flex justify-evenly">
                    <div>
                        <h1 className="text-[40px] text-left pt-5">INTELLIGENT AI AGENT FOR CUSTOMIZED WORKFLOWS</h1>
                        <p className="text-[25px] text-left pt-7.5 pb-10">
                            SecuriVA's integrated AI agent allows you to effortlessly construct automated workflows and generate security insights.
                        </p>
                        <button
                            className="font-[20px] w-50 h-17.5 bg-red-500"
                        >
                            Start Free Trial
                        </button>
                    </div>

                    <div style={{}}>
                        <img
                            src="/agent.png"
                            alt="agent_page_image"
                            className="h-auto w-300 px-7.5 py-7.5"
                        />
                    </div>
                </div>
            </header>

            <h1 style={{ textAlign: "center" }}>Meet AVA, SecuriVA's Intelligent AI Agent</h1>

            <div className="graph text-black">

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