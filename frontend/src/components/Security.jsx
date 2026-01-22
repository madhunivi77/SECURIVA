import Card from "./Card";
function Security() {
    return (
        <div>
            {/* ---------- HEADER ---------- */}
            <header className="hero section-min-height">
                <div className="hero-content flex justify-evenly">
                    <div>
                        <h1 className="text-[40px] text-left pt-5">PROACTIVE SECURITY MEASURES TO PROTECT YOUR BUSINESS</h1>
                        <p className="text-[25px] text-left pt-7.5 pb-10">
                        SecuriVA's cyber defense core secures your business operations by providing a suite of real time monitoring appliances to give you peace of mind in a world of evolving cyber threats.
                        </p>
                        <button
                            className="font-[20px] w-50 h-17.5 bg-red-500"
                        >
                        Start Free Trial
                        </button>
                    </div>

                    <div style={{}}>
                        <img
                        src="/Security_shield.png"
                        alt="security_page_image"
                        className="h-auto w-300 px-7.5 py-7.5"
                        />
                    </div>
                </div>
            </header>
            <h1 className="text-center">Protection Layers</h1>
            <div
                className="gap-12.5 mx-0 my-auto p-20 text-black"
                style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(3, 1fr)",
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
            <h1 className="text-center" ><span className="text-blue-300 text-[.75em]">▼</span> ALL CONNECTED TO  <span className="text-blue-300 text-[.75em]">▼</span></h1>
            <div 
                className="justify-center text-black"
            >
                <Card image={""} title={"SECURIVA AI ENGINE"} text={"Real-time monitoring & Automation Predict • Block • Secure • Recover"}/>
            </div>
        </div>
        
    )
}

export default Security;