import { BadgeCheck, CircleDollarSign, GlobeLock, Lock, Phone, Play, SearchCode, ShieldAlert, Target, Handshake, Files, Cctv, BrickWallShield, Expand, ChartNoAxesCombined } from "lucide-react";
import { Link } from "react-router-dom";
import CapabilityCard from "../components/CapabilityCard";
import SolutionCard from "../components/SolutionCard";
import ReasonCard from "../components/ReasonCard";
import SymmetricalChecklist from "../components/SymmetricalChecklist";
import Checklist from "../components/Checklist";

const reasons = [
    {
        icon: BrickWallShield,
        label: "Integrated Security Across Platforms",
        description: "AI, automation, and communication tools all benefit from embedded protection.",
    },
    {
        icon: Cctv,
        label: "Real-Time Threat Intelligence",
        description: "AI identifies and responds to potential risks before damage occurs."
    },
    {
        icon: BadgeCheck,
        label: "Regulatory Confidence",
        description: "Compliant with GDPR, HIPAA, PCI-DSS standards across all operations."
    },
    {
        icon: Expand,
        label: "Scalable for All Industries",
        description: "Healthcare, finance, e-commerce, education, government, SMBs, agriculture, nonprofits, and more."
    },
    {
        icon: ChartNoAxesCombined,
        label: "Continuous Improvement",
        description: "Security frameworks are constantly updated to meet evolving threats."
    }
]

export default function Cybersecurity() {
    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900">

            {/* ---------- HERO ---------- */}
            <section className="hero py-24 bg-linear-to-br bg-[#0a0f1f] text-white">
                <div className="hero-content text-center max-w-4xl">
                    <div>
                        <h1 className="text-5xl font-bold mb-6">Cybersecurity</h1>
                        <p className="text-xl opacity-90">
                            At SecuriVA, cybersecurity is not an afterthought—it is embedded into every layer of the platform. From AI agents to automation workflows and VPN Secure Access, your data, communications, and customer interactions are protected, monitored, and compliant at all times.
                        </p>
                    </div>
                </div>
            </section>

            <section className="relative overflow-hidden">
                <div className="relative w-full h-[400px] overflow-hidden bg-black mx-auto">
                    <video
                        autoPlay
                        loop
                        muted
                        playsInline
                        className="absolute top-0 left-0 w-full object-cover opacity-40"
                    >
                        <source src="Cybersecurity_video.mp4" type="video/mp4" />
                        Your browser does not support the video tag.
                    </video>

                    <div className="absolute top-0 left-0 w-full h-64 bg-gradient-to-b from-[#0a0f1f] via-[#0a0f1f]/60 to-transparent pointer-events-none"></div>

                    <div className="absolute bottom-0 left-0 w-full h-64 bg-gradient-to-t from-[#131827] via-gray-black/60 to-transparent pointer-events-none"></div>

                    {/* Content */}
                    <div className="relative max-w-6xl mx-auto -mt-10">
                        <h2 className="subheading">Protect Your Business with AI-Driven Security and Compliance</h2>
                        <p className="text-center card p-12 mx-[15%] backdrop-blur bg-gray-800/50 shadow-lg text-xl">
                            SecuriVA ensures organizations of all sizes, across all industries, operate safely in a digital-first world.
                        </p>
                    </div>
                </div>
            </section>

            <section className="flex flex-col gap-5 mb-5 -mt-20 mx-[15%]">
                <h2 className="subheading pt-10 mb-12 text-center">Cybersecurity Fundamentals</h2>
                <CapabilityCard icon={GlobeLock} label={"Encryption Protocols"} description={"All communications, transactions, and stored data are encrypted using industry-standard methods, ensuring confidentiality and integrity."} />
                <CapabilityCard icon={ShieldAlert} label={"Threat Detection"} description={"AI-driven monitoring continuously scans for anomalies, suspicious behavior, and potential cyberattacks in real-time."} />
                <CapabilityCard icon={SearchCode} label={"Vulnerability Analysis"} description={"Regular automated and manual security audits identify weak points, with actionable recommendations to prevent breaches."} />
                <CapabilityCard icon={BadgeCheck} label={"Compliance Standards Knowledge"} description={"SecuriVA aligns with regulations including GDPR, HIPAA, and PCI-DSS, ensuring your data handling meets legal and industry requirements."} />
            </section>

            <h2 className="subheading">Value Proposition</h2>
            <p className="subtext">SecuriVA transforms cybersecurity from a reactive function into a proactive operational advantage, giving businesses confidence in AI-driven operations.</p>

            <section className="gap-5 my-5 mx-[15%]">
                <SymmetricalChecklist heading={"Cybersecurity Protection:"} items={
                    [
                        "Real-time threat detection",
                        "Data encryption at rest and in transit",
                        "Compliance with GDPR, HIPAA, PCI-DSS",
                        "Integrated into all SecuriVA services (AI Virtual Agent, Text Agent, VPN, Automation Workflows)"
                    ]
                } />
            </section>

            <section className="flex flex-col gap-5 my-5 mx-[15%]">
                <SolutionCard number={"01"} icon={Target} label={"Core Activities"} content={
                    <div>
                        <h3 className="text-lg text-gray-500 my-3 leading-relaxed dark:text-gray-400">Cybersecurity and Compliance Framework</h3>
                        <Checklist items={[
                            "Real-time threat detection",
                            "Encrypted data management",
                            "Compliance reporting across all platforms and integrations"
                        ]} size={"3.5"}/>

                        <h3 className="text-lg text-gray-500 my-3 leading-relaxed dark:text-gray-400">Cybersecurity Monitoring & Upgrades</h3>
                        <Checklist items={[
                            "Continuous monitoring of system health and activity",
                            "Automated alerts for anomalous behaviors",
                            "Regular security patches and upgrades to meet evolving threats",
                            "Ensures ongoing regulatory compliance"
                        ]} size={"3.5"}/>
                    </div>
                }
                />
                <SolutionCard number={"02"} icon={CircleDollarSign} label={"Cost Structure"} description={"Cybersecurity & Compliance investments include:"} points={
                    [
                        "Ongoing audits and vulnerability testing",
                        "Encryption implementation and updates",
                        "Deployment of advanced protection tools",
                        "Compliance reporting and certification support"
                    ]}
                    footer={"This ensures businesses maintain robust protection without unexpected costs."}
                />

                <SolutionCard number={"03"} icon={Handshake} label={"Partnerships"} description={"SecuriVA collaborates with top-tier cybersecurity vendors to enhance protection capabilities:"} points={[
                            "Providers of security frameworks",
                            "SIEM (Security Information and Event Management) solutions",
                            "Encryption specialists",
                            "Vulnerability monitoring and testing vendors"
                        ]} footer={"These partnerships ensure best-in-class security across every integration and workflow."} />

                <SolutionCard number={"04"} icon={Files} label={"Resources"} description={"SecuriVA equips your team with the following security resources:"} points={[
                    "Cybersecurity Frameworks", 
                    "SIEM tools for continuous threat monitoring", 
                    "Encryption protocols for data in transit and at rest", 
                    "Regular vulnerability testing and reporting", 
                    "Training materials and documentation for compliance and incident response"
                    ]} footer={"With these resources, organizations can build internal security competence while relying on SecuriVA’s advanced protection."}/>
            </section>

            {/* Why */}
            <h2 className="subheading">Why SecuriVA Cybersecurity Stands Out</h2>

            <section className="gap-5 my-5 mx-[15%]">
                {/* Reason Cards */}
                <div className="flex flex-wrap justify-center gap-3 mb-10">
                    {reasons.map((reason) => (
                        <ReasonCard key={reason.label} {...reason} />
                    ))}
                </div>
            </section>

            {/* Call to Action */}
            <section className="px-8 py-16 text-center">
                <h2 className="text-4xl font-normal text-gray-900 mb-3 dark:text-white">
                    Protect Your Business Today
                </h2>
                <p className="text-2xl font-light text-gray-500 mb-10 max-w-xl mx-auto dark:text-gray-400">
                    Ensure your AI workflows, automation processes, and customer interactions are secure, compliant, and monitored in real-time.
                </p>
                <div className="flex flex-wrap justify-center gap-3">
                    <Link to={"/contact"}>
                        <button className="flex items-center gap-2 rounded-xl bg-red-500 px-6 py-3 text-[14px] font-medium text-white transition-colors hover:bg-red-400">
                            <Play className="h-4 w-4 fill-white stroke-none" />
                            Request a Demo
                        </button>
                    </Link>
                    <Link to={"/cybersecurity"}>
                        <button onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })} className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-6 py-3 text-[14px] font-medium text-gray-800 transition-colors hover:border-gray-300 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:hover:border-gray-600 dark:hover:bg-gray-800">
                            <Lock className="h-4 w-4 stroke-gray-500 dark:stroke-gray-400" strokeWidth={1.5} />
                            Explore Security Documentation
                        </button>
                    </Link>
                    <Link to={"/contact"}>
                        <button className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-6 py-3 text-[14px] font-medium text-gray-800 transition-colors hover:border-gray-300 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:hover:border-gray-600 dark:hover:bg-gray-800">
                            <Phone className="h-4 w-4 stroke-gray-500 dark:stroke-gray-400" strokeWidth={1.5} />
                            Contact our Cybersecurity Team
                        </button>
                    </Link>
                </div>
            </section>

        </div>
    );
}