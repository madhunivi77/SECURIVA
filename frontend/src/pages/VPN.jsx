import { ArrowLeftRight, Brain, BrainCircuit, ClipboardList, GlobeLock, HouseWifi, KeyRound, Lock, MessageSquare, Mic, Network, Phone, PocketKnife, Share2, ShieldAlert, ShieldCheck, Trophy, Users, Workflow, WorkflowIcon, X, Zap } from "lucide-react";
import SolutionCard from "../components/SolutionCard";
import CapabilityCard from "../components/CapabilityCard";
import SymmetricalChecklist from "../components/SymmetricalChecklist";
import Checklist from "../components/Checklist";
import ReasonCard from "../components/ReasonCard";

const reasons = [
    {
        icon: Users,
        label: "Remote & Hybrid Teams",
        description: "Secure access to internal systems, CRM, databases, and dashboards—no matter where staff work.",
    },
    {
        icon: ClipboardList,
        label: "Highly Regulated Industries",
        description: "Healthcare, finance, government, and legal operations get a protected environment for sensitive processes."
    },
    {
        icon: BrainCircuit,
        label: "AI Automation Security",
        description: "All AI-driven tasks remain private and encrypted."
    },
    {
        icon: ArrowLeftRight,
        label: "Cross-Border Operations",
        description: "International teams connect safely to the same protected ecosystem."
    },
    {
        icon: WorkflowIcon,
        label: "API-Driven Business Workflows",
        description: "Secure data exchange between tools, cloud platforms, and AI agents."
    }
]


export default function VPN() {
    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900">

            {/* ---------- HERO ---------- */}
            <section className="hero pt-24 bg-linear-to-br bg-[#0a0f1f] text-white">
                <div className="hero-content text-center max-w-4xl">
                    <div>
                        <h1 className="text-5xl font-bold mb-6">VPN Secure Access</h1>
                        <p className="text-xl opacity-90">
                            VPN Secure Access transforms SecuriVA from an AI platform into a secure operating environment for the entire organization
                        </p>
                    </div>
                </div>
            </section>

            <section className="relative overflow-hidden">
                <div className="relative w-full h-[600px] overflow-hidden bg-black mx-auto">
                    <video
                        autoPlay
                        loop
                        muted
                        playsInline
                        className="absolute top-0 left-0 w-full h-[70%] object-cover opacity-40"
                    >
                        <source src="VPN_video.mp4" type="video/mp4" />
                        Your browser does not support the video tag.
                    </video>

                    <div className="absolute top-0 left-0 w-full h-64 bg-gradient-to-b from-[#0a0f1f] via-[#0a0f1f]/60 to-transparent pointer-events-none"></div>

                    <div className="absolute bottom-0 left-0 w-full h-64 bg-gradient-to-t from-[#131827] via-gray-black/60 to-transparent pointer-events-none"></div>

                    {/* Content */}
                    <div className="relative max-w-6xl mx-auto pt-10">
                        <h2 className="subheading">Protect Your Business with AI-Driven Security and Compliance</h2>
                        <p className="text-center card p-2 mx-[15%] backdrop-blur bg-gray-800/50 shadow-lg text-xl">
                            VPN Secure Access is the network-layer protection module of SecuriVA, delivering
                            encrypted connectivity, zero-trust access, and AI-driven threat detection for
                            distributed teams, cloud systems, and sensitive workflows.
                        </p>
                        {/* Unlike traditional
                            virtual assistants or automation platforms, SecuriVA embeds a native VPN
                            infrastructure, ensuring that every voice interaction, text automation, API
                            communication, and workflow execution happens inside a protected, private network. */}
                    </div>
                </div>
            </section>

            <section className="relative overflow-hidden px-8 pb-6 -mt-20">
                <h2 className="subheading">Integrating VPN Into SecuriVA</h2>
                <p class="text-xl font-light text-gray-500 mb-8 text-center dark:text-gray-400 mx-[15%]">VPN Secure Access is seamlessly integrated across all SecuriVA components:</p>
                <div className="flex flex-wrap gap-3 mb-6 mx-[15%]">
                    {[
                        {
                            icon: Mic,
                            label: "AI Agent Voice",
                            description: "All voice interactions, call routing, identity checks, and backend queries occur inside the encrypted network.",
                        },
                        {
                            icon: MessageSquare,
                            label: "Text Agent",
                            description: "Messages, emails, documents, forms, and knowledge base lookups are shielded from external interception.",
                        },
                        {
                            icon: Lock,
                            label: "Cybersecurity Engine",
                            description: "VPN traffic is continuously scanned by SecuriVA’s AI threat intelligence.",
                        },
                        {
                            icon: Zap,
                            label: "Automation Workflows",
                            description: "Every automated task—internal or external—executes through a private, encrypted tunnel.",
                        },
                        {
                            icon: Network,
                            label: "System Integrations (Gmail, WhatsApp, Salesforce, Banking APIs, Cloud Platforms, OpenAI, etc.)",
                            description: "All API calls route through a secure network layer for maximum confidentiality."
                        }
                    ].map((card) => (
                        <CapabilityCard className="sm:min-w-[35%] min-w-[70%]" key={card.label} {...card} />
                    ))}
                </div>
                <p class="text-xl font-light text-gray-500 text-center dark:text-gray-400 mx-[15%]">This positioning makes the VPN a core foundation of SecuriVA, not a separate tool.</p>
            </section>

            <section className="flex flex-col gap-5 py-5 mx-[15%]">

                <h2 className="subheading">Features of SecuriVA VPN</h2>
                <SolutionCard number={"01"} icon={Workflow} label={"One-Click Secure Browsing"} description={"All communications—including email, chat, calls, and API requests—are routed through a secure encrypted tunnel with a single activation. This protects all operational and customer data from interception, leakage, or unauthorized access."} points={
                    [
                        "Encrypted data transport",
                        "Hidden IP and traffic anonymization",
                        "Automatic tunnel activation for AI workflows",
                        "Continuous monitoring for unusual activity"
                    ]}
                />

                <SolutionCard number={"02"} icon={ShieldAlert} label={"AI Threat Detection Inside the VPN"} description={"SecuriVA introduces a unique capability: AI-driven, real-time scanning of all VPN traffic. Instead of merely encrypting traffic, the system actively analyzes it for anomalous patterns such as:"} points={
                    [
                        "Suspicious packet signatures",
                        "Malicious API requests",
                        "Identity fraud attempts",
                        "Bot or automated attack patterns",
                        "Data exfiltration signals"
                    ]}
                    footer={"This elevates standard VPN technology into proactive cybersecurity intelligence."}
                />

                <SolutionCard number={"03"} icon={Share2} label={"Adaptive Routing"} description={"The VPN dynamically chooses the fastest and safest server using AI-driven routing optimization and adaptive logic based on:"} points={
                    [
                        "Server load",
                        "Latency",
                        "Geographical constraints",
                        "Detected threats",
                        "Compliance requirements"
                    ]}
                    footer={"This ensures stable performance even in global, multi-branch, or hybrid environments."}
                />

                <SolutionCard number={"04"} icon={ShieldCheck} label={"Compliance-Ready Protection"} description={"VPN Secure Access supports organizations facing strict regulatory frameworks such as:"} points={
                    [
                        "GDPR",
                        "HIPAA",
                        "PCI-DSS",
                        "Financial data residency rules",
                        "Government and public-sector security standards"
                    ]}
                    footer={"Data remains protected throughout remote, hybrid, or distributed operations, enabling compliance without complex configurations."}
                />

                <SolutionCard number={"05"} icon={KeyRound} label={"Integrated Multi-Factor Authentication (MFA)"} description={"For users accessing sensitive dashboards, financial systems, or mission-critical automation tools, SecuriVA’s VPN enforces:"} points={
                    [
                        "MFA login",
                        "Zero-trust device checks",
                        "Identity verification",
                        "Dynamic session authorization",
                    ]}
                    footer={"This ensures only trusted personnel can access protected environments."}
                />

            </section>

            <section className="flex flex-col gap-5 py-5 mx-[15%]">
                <h2 className="subheading">Why SecuriVA VPN Is Valuable</h2>
                <SolutionCard icon={PocketKnife} label={"All-in-One Platform"} description={"Businesses get a single unified environment combining:"} points={
                    [
                        "AI virtual assistants (voice & text)",
                        "Automation workflows",
                        "Cybersecurity",
                        "Data protection",
                        "Built-in VPN network security"
                    ]}
                    footer={"No need for separate subscriptions, vendors, or overhead."}
                />

                <SolutionCard icon={HouseWifi} label={"Eliminates the Need for External VPN Services"} description={"Organizations avoid paying for, maintaining, or integrating third-party VPN solutions. SecuriVA covers:"} points={
                    [
                        "Secure remote work",
                        "Secure access to internal systems",
                        "Protected cloud usage",
                        "Confidential workflow execution",
                    ]}
                    footer={"Everything is native, preconfigured, and optimized."}
                />

                <SolutionCard icon={Trophy} label={"Differentiates SecuriVA in the VA / Automation Market"} description={"Most AI platforms offer:"} content={
                    <div>
                        <ul className="flex flex-col gap-1.5 pb-2">
                            {[
                                "AI only",
                                "Automation only",
                                "Chatbots only",
                                "Basic Security"
                            ].map((item) => (
                                <li key={item} className={`flex items-start gap-2 text-lg text-gray-700 dark:text-gray-300`}>
                                    <X className={`mt-2 h-3.5 w-3.5 shrink-0 stroke-red-500 dark:stroke-blue-400" strokeWidth={2} `} />
                                    {item}
                                </li>
                            ))}
                        </ul>
                        <p className="text-lg text-gray-500 mb-3 leading-relaxed dark:text-gray-400">SecuriVA goes far beyond with network-layer protection integrated at the core, offering:</p>
                        <Checklist items={[
                            "AI + Cybersecurity + Private Network + Automation",
                            "A full secure infrastructure for enterprise-grade operations",
                            "Compliance-centered architecture"
                        ]} size={"3.5"} />
                    </div>
                }
                    footer={"This makes SecuriVA uniquely positioned as a Secure AI Operations Platform."}
                />
            </section>

            <section className="flex flex-col gap-5 py-5 mx-[15%]">
                <h2 className="subheading">Key Use Cases</h2>
                <div className="flex flex-wrap justify-center gap-3 mb-10">
                    {reasons.map((reason) => (
                        <ReasonCard key={reason.label} {...reason} />
                    ))}
                </div>
            </section>

            <section className="flex flex-col gap-5 py-5 mx-[15%]">
                <h2 className="subheading">Final Value Proposition</h2>
                <CapabilityCard icon={GlobeLock} label={"VPN Secure Access is not simply a connectivity feature—it is a strategic security layer that transforms SecuriVA into a comprehensive enterprise automation and protection platform."} description={"You get:"} content=
                    {
                        <SymmetricalChecklist items={[
                            "End-to-end encrypted operations",
                            "AI-augmented threat detection",
                            "Compliance-ready infrastructure",
                            "Zero-trust access management",
                            "Fully integrated protected workflows",
                            "No third-party VPN required"
                        ]} />
                    } />
            </section>
        </div>
    );
}