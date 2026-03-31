import { Play, Workflow, Phone, Mail, MessageCircle, File, Network, Brain, Expand, Lock, CircleDollarSign } from "lucide-react";
import { Link } from "react-router-dom";
import CapabilityCard from "../components/CapabilityCard";
import SymmetricalChecklist from "../components/SymmetricalChecklist";
import ReasonCard from "../components/ReasonCard";

const reasons = [
    {
        icon: Network,
        label: "Cross-Platform Support",
        description: "Works with email, chat apps, websites, and third-party APIs.",
    },
    {
        icon: Brain,
        label: "AI-Driven Accuracy",
        description: "Context-aware responses reduce mistakes and improve engagement.",
    },
    {
        icon: Expand,
        label: "Scalable Across Industries",
        description: "Suitable for healthcare, finance, e-commerce, SMBs, education, government, and more.",
    },
    {
        icon: Lock,
        label: "End-to-End Security",
        description: "All data handled inside SecuriVA’s secure ecosystem.",
    },
    {
        icon: CircleDollarSign,
        label: "Time and Cost Savings",
        description: "Streamlines operations while lowering operational costs.",
    },
];

export default function AgentText({ }) {
    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900">

            {/* ---------- HERO ---------- */}
            <section className="hero py-24 bg-linear-to-br from-blue-900 to-black text-white">
                <div className="hero-content text-center max-w-4xl">
                    <div>
                        <h1 className="text-5xl font-bold mb-6">
                            Text AI Agent: Intelligent Automation for Email, Chat, and Messaging
                        </h1>
                        <p className="text-xl opacity-90">
                            The Text AI Agent is SecuriVA’s intelligent automation module designed to streamline business communication and workflow. It allows organizations to save time, reduce errors, and improve responsiveness across multiple channels—all while ensuring data security and compliance.
                        </p>
                    </div>
                </div>
            </section>

            <h2 className="subheading">
                Automation Capabilities
            </h2>

            <section className="flex flex-col gap-5 my-5 mx-[15%]">
                <CapabilityCard icon={Mail} label={"Email responses and follow-ups"} description={"Automatically drafts and sends context-aware replies, reducing manual effort and ensuring timely communication."} />
                <CapabilityCard icon={MessageCircle} label={"Chat interactions on WhatsApp, Gmail, and websites"} description={"Handles customer inquiries, support chats, and internal messaging with AI-driven responses."} />
                <CapabilityCard icon={File} label={"Document handling, analysis, and data extraction"} description={"Processes attachments, extracts relevant data, summarizes content, and integrates results into workflows."} />
                <CapabilityCard icon={Workflow} label={"API-based task automation across platforms"} description={"Connects with your existing systems and services to automate repetitive tasks, from CRM updates to cloud storage actions."} />
            </section>

            <section className="gap-5 my-5 mx-[15%]">
                <SymmetricalChecklist heading={"Key Advantages"} items={
                    [
                        "Reduces manual workloads",
                        "Improves customer response times",
                        "Integrates with workflow automation tools",
                        "Secure and compliant with data privacy standards"
                    ]
                } />
            </section>

            <h2 className="subheading">
                Why Choose Text AI Agent
            </h2>

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
                    Boost Your Business Communication with AI
                </h2>
                <p className="text-2xl font-light text-gray-500 mb-10 max-w-xl mx-auto dark:text-gray-400">
                    Automate emails, chats, document processing, and API tasks securely and efficiently.
                </p>
                <div className="flex flex-wrap justify-center gap-3">
                    <Link to={"/contact"}>
                        <button className="flex items-center gap-2 rounded-xl bg-red-500 px-6 py-3 text-[14px] font-medium text-white transition-colors hover:bg-red-400">
                            <Play className="h-4 w-4 fill-white stroke-none" />
                            Request a Demo
                        </button>
                    </Link>
                    <Link to={"/contact"}>
                        <button onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })} className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-6 py-3 text-[14px] font-medium text-gray-800 transition-colors hover:border-gray-300 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:hover:border-gray-600 dark:hover:bg-gray-800">
                            <Workflow className="h-4 w-4 stroke-gray-500 dark:stroke-gray-400" strokeWidth={1.5} />
                            Learn How Text AI Agent Integrates with Your Workflows
                        </button>
                    </Link>
                    <Link to={"/pricing"}>
                        <button className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-6 py-3 text-[14px] font-medium text-gray-800 transition-colors hover:border-gray-300 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:hover:border-gray-600 dark:hover:bg-gray-800">
                            <Phone className="h-4 w-4 stroke-gray-500 dark:stroke-gray-400" strokeWidth={1.5} />
                            Contact Our Team for More Information
                        </button>
                    </Link>
                </div>
            </section>
        </div>
    );
}