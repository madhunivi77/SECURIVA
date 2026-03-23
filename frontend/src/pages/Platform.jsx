import { Link } from "react-router-dom";
import Sponsors from "../components/Sponsors";
import {
    Mic, ShieldCheck, MessageSquare, Lock,
    CheckCircle2, Users, Play, CircleDollarSign,
    LayoutDashboard, Zap, Phone
} from "lucide-react";
import { useTheme } from "../context/ThemeContext";
const platforms = [
    {
        number: "01",
        icon: Mic,
        label: "AI Agent Voice",
        tagline: "Natural Voice Intelligence for All Interactions",
        description: "The AI Agent Voice provides autonomous, real-time voice assistance powered by advanced conversational intelligence. It can replace or augment human phone agents, streamline internal communication, and automate workflows across departments.",
        capabilities: [
            "Human-like conversational voice responses",
            "24/7 virtual phone support",
            "Automated call handling, routing, and triage",
            "Appointment scheduling and reminders",
            "Order management, follow-ups, and notifications",
            "Secure identity verification via voice",
            "Integration with CRM, ticketing, and internal systems",
        ],
        idealFor: [
            "Customer support centers",
            "Healthcare clinics",
            "Financial institutions",
            "Government agencies",
            "E-commerce customer service",
            "Education and campus services",
        ],
        value: [
            "Reduce support costs",
            "Enhance response speed",
            "Maintain consistent, high-quality service",
            "Scale operations instantly",
        ],
    },
    {
        number: "02",
        icon: ShieldCheck,
        label: "Cybersecurity",
        tagline: "Security Core Built Into Every Interaction",
        description: "Cybersecurity in Securiva is not an add-on—it is the foundation of the platform. Every AI interaction, workflow, voice call, and automation is secured using a robust, zero-trust architecture.",
        capabilities: [
            "Multi-layer threat detection and prevention",
            "Identity and access management",
            "Real-time threat monitoring",
            "Data encryption (at rest & in transit)",
            "Secure API integrations",
            "Incident response tools",
            "Anti-fraud protections",
            "Compliance alignment (industry-specific)",
        ],
        idealFor: [
            "Finance",
            "Healthcare",
            "Government",
            "E-commerce",
            "Any organization requiring strict data protection",
        ],
        value: [
            "Stronger protection against cyber threats",
            "Full data integrity and confidentiality",
            "Compliance-ready environment",
            "Reduced risk and operational exposure",
        ],
    },
    {
        number: "03",
        icon: MessageSquare,
        label: "Text Agent",
        tagline: "Intelligent Text Automation for All Channels",
        description: "The Text Agent automatically manages conversations across multiple written channels, providing instant, personalized, and secure messaging.",
        capabilities: [
            "AI chat assistance for websites, mobile apps, portals",
            "Automated email responses",
            "Workflow-triggered messaging",
            "SMS engagement and notifications",
            "Case management and ticket updates",
            "Form autofill, document guidance, and onboarding support",
            "Knowledge-based assistance",
        ],
        idealFor: [
            "Customer service",
            "Admissions offices",
            "Online retail",
            "Administrative offices",
            "Nonprofit engagement",
            "IT and helpdesk operations",
        ],
        value: [
            "24/7 instant text communication",
            "Lower workload on human agents",
            "Improved customer satisfaction",
            "Faster data collection and process automation",
        ],
    },
    {
        number: "04",
        icon: Lock,
        label: "VPN Secure Access",
        tagline: "Encrypted, Private, Zero-Trust Access Anywhere",
        description: "VPN Secure Access ensures that all remote staff, partners, volunteers, and contractors connect safely to your systems from any location.",
        capabilities: [
            "Encrypted remote access",
            "Zero-trust connection enforcement",
            "Secure login to cloud and on-prem systems",
            "Multi-device configuration (desktop/mobile)",
            "Traffic anonymization",
            "Protection for sensitive workflows and AI interactions",
        ],
        idealFor: [
            "Distributed teams",
            "Remote support agents",
            "Government and regulated sectors",
            "Organizations handling private data",
            "Cross-border teams (international operations)",
        ],
        value: [
            "Protect internal systems from unauthorized access",
            "Enable safe remote work",
            "Guarantee compliance for all connected users",
        ],
    },
];

const advantages = [
    "Full automation of customer and internal operations",
    "Enterprise-level cybersecurity",
    "Compliance-first data protection",
    "Voice + text AI unified in a single ecosystem",
    "Safe access for remote work and hybrid teams",
    "Scalable for SMBs, enterprises, and governments",
];

const PlatformCard = ({ number, icon: Icon, label, tagline, description, capabilities, idealFor, value }) => {
    const { theme } = useTheme();
    return (
        <div className={`rounded-2xl border border-gray-100 ${theme.bg} p-6 hover:border-gray-200 transition-colors dark:border-gray-800 dark:hover:border-gray-700`}>

            {/* Card Header */}
            <div className="flex gap-4 mb-5">
                <div className="flex flex-col items-center gap-2 pt-1">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-950">
                        <Icon className="h-5 w-5 stroke-blue-600 dark:stroke-blue-400" strokeWidth={1.5} />
                    </div>
                    <span className="text-xl font-medium tabular-nums text-gray-300 dark:text-gray-700">{number}</span>
                </div>
                <div>
                    <h3 className="text-xl font-medium text-gray-900 dark:text-white mb-0.5">{label}</h3>
                    <p className="text-[19px] italic text-blue-600 dark:text-blue-400 mb-2">{tagline}</p>
                    <p className="text-lg text-gray-500 leading-relaxed dark:text-gray-400">{description}</p>
                </div>
            </div>

            <div className="border-t border-gray-100 dark:border-gray-800 mb-5" />

            {/* Three Columns */}
            <div className="flex flex-wrap gap-6">

                {/* Capabilities */}
                <div className="flex-1 min-w-[180px]">
                    <p className="text-xl font-medium uppercase tracking-widest text-gray-400 mb-3">Capabilities</p>
                    <ul className="flex flex-col gap-1.5">
                        {capabilities.map((item) => (
                            <li key={item} className="flex items-start gap-2 text-lg text-gray-700 dark:text-gray-300">
                                <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 stroke-blue-500 dark:stroke-blue-400" strokeWidth={2} />
                                {item}
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Ideal For */}
                <div className="flex-1 min-w-[140px]">
                    <p className="text-xl font-medium uppercase tracking-widest text-gray-400 mb-3">Ideal For</p>
                    <ul className="flex flex-col gap-1.5">
                        {idealFor.map((item) => (
                            <li key={item} className="flex items-start gap-2 text-lg text-gray-700 dark:text-gray-300">
                                <Users className="mt-0.5 h-3.5 w-3.5 shrink-0 stroke-gray-400 dark:stroke-gray-600" strokeWidth={2} />
                                {item}
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Value */}
                <div className="flex-1 min-w-[140px]">
                    <p className="text-xl font-medium uppercase tracking-widest text-gray-400 mb-3">Value</p>
                    <ul className="flex flex-col gap-1.5">
                        {value.map((item) => (
                            <li key={item} className="flex items-start gap-2 text-lg text-gray-700 dark:text-gray-300">
                                <Zap className="mt-0.5 h-3.5 w-3.5 shrink-0 stroke-amber-500 dark:stroke-amber-400" strokeWidth={2} />
                                {item}
                            </li>
                        ))}
                    </ul>
                </div>

            </div>
        </div>
    );
}

export default function Platform() {

    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900">

            {/* ---------- HERO ---------- */}
            <section className="hero py-24 bg-linear-to-br from-blue-900 to-black text-white">
                <div className="hero-content text-center max-w-4xl">
                    <div>
                        <h1 className="text-5xl font-bold mb-6">Platform</h1>
                        <p className="text-xl opacity-90">
                            Securiva provides an integrated platform that combines secure communication, advanced
                            AI automation, and enterprise-grade protection. Each component works seamlessly within
                            the Securiva ecosystem to deliver a unified environment for voice intelligence, text
                            automation, cyber defense, and secure access.
                        </p>
                    </div>
                </div>
            </section>

            <section className="px-8 py-16 max-w-4xl mx-auto">

                {/* Header */}
                <div className="mb-12 text-center">
                    <h2 className="text-3xl font-normal text-gray-900 mb-3 dark:text-white">
                        A Unified Intelligent Platform for Secure, Automated, AI-Driven Operations
                    </h2>
                    <p className="text-xl font-light text-gray-500 max-w-xl mx-auto leading-relaxed dark:text-gray-400">
                        Our platform is designed to support organizations of all sizes—across all industries—seeking to modernize their operations, protect their data, and elevate customer engagement.
                    </p>
                </div>

                <h2 className="text-center text-3xl font-normal text-gray-900 mb-3 dark:text-white">
                    Platform Components
                </h2>
                {/* Platform Cards */}
                <div className="flex flex-col gap-4 mb-8">
                    {platforms.map((platform) => (
                        <PlatformCard key={platform.number} {...platform} />
                    ))}
                </div>

                {/* Unified Architecture Note */}
                <div className="rounded-2xl border border-gray-100 bg-gray-50 p-6 mb-4 dark:border-gray-800 dark:bg-gray-900">
                    <div className="flex gap-3 mb-4">
                        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-950">
                            <LayoutDashboard className="h-4 w-4 stroke-blue-600 dark:stroke-blue-400" strokeWidth={1.5} />
                        </div>
                        <div>
                            <h3 className="text-xl font-medium text-gray-900 dark:text-white mb-0.5">Unified Platform Architecture</h3>
                            <p className="text-[19px] text-gray-500 dark:text-gray-400 leading-relaxed">
                                Securiva integrates all four components into a single, cohesive ecosystem — eliminating the need for multiple disconnected tools, reducing cost, improving security, and accelerating deployment.
                            </p>
                        </div>
                    </div>
                    <ul className="flex flex-col gap-2 pl-12">
                        {[
                            "AI Agent Voice and Text Agent work simultaneously to handle voice and text interactions across all channels.",
                            "Cybersecurity provides continuous protection for every automation, conversation, and workflow.",
                            "VPN Secure Access ensures all internal operations and external connections are fully encrypted.",
                        ].map((item) => (
                            <li key={item} className="flex items-start gap-2 text-lg text-gray-600 dark:text-gray-400">
                                <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 stroke-blue-500 dark:stroke-blue-400" strokeWidth={2} />
                                {item}
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Why Organizations Choose Securiva */}
                <div className="rounded-2xl border border-blue-100 bg-blue-50 p-6 dark:border-blue-900 dark:bg-blue-950">
                    <h3 className="text-xl font-medium text-gray-900 dark:text-white mb-1">Why Organizations Choose Securiva Platform</h3>
                    <p className="text-[19px] text-gray-500 dark:text-blue-300 mb-4">One platform, four capabilities, infinite applications:</p>
                    <ul className="flex flex-col gap-x-8 gap-y-2">
                        {advantages.map((item) => (
                            <li key={item} className="flex items-center gap-2 text-lg text-gray-700 dark:text-blue-200">
                                <CheckCircle2 className="h-3.5 w-3.5 shrink-0 stroke-blue-500 dark:stroke-blue-400" strokeWidth={2} />
                                {item}
                            </li>
                        ))}
                    </ul>
                </div>

            </section>

            {/* Call to Action */}
            <section className="px-8 py-16 text-center">
                <h2 className="text-4xl font-normal text-gray-900 mb-3 dark:text-white">
                    Experience the Power of the SecuriVA Platform
                </h2>
                <p className="text-2xl font-light text-gray-500 mb-10 max-w-xl mx-auto dark:text-gray-400">
                    Modernize Your Organization with the All-in-One Securiva Platform
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
                            <Phone className="h-4 w-4 stroke-gray-500 dark:stroke-gray-400" strokeWidth={1.5} />
                            Contact Sales
                        </button>
                    </Link>
                    <Link to={"/pricing"}>
                        <button className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-6 py-3 text-[14px] font-medium text-gray-800 transition-colors hover:border-gray-300 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:hover:border-gray-600 dark:hover:bg-gray-800">
                            <CircleDollarSign className="h-4 w-4 stroke-gray-500 dark:stroke-gray-400" strokeWidth={1.5} />
                            Explore Pricing
                        </button>
                    </Link>
                </div>
            </section>

            <Sponsors className="bg-white mt-10 pt-5 text-center text-black text-3xl" />
        </div>
    );
}