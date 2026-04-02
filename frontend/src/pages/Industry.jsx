import { BadgeCheckIcon, Brain, CheckCircle2, Factory, Lock } from "lucide-react";
import SolutionCard from "../components/SolutionCard";
import { useTheme } from "../context/ThemeContext";
import IndustryCard from "../components/IndustryCard";
import SymmetricalChecklist from "../components/SymmetricalChecklist";
export default function Industry() {
    const { theme } = useTheme();
    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900">

            {/* ---------- HERO ---------- */}
            <section className="hero py-24 bg-linear-to-br bg-[#0a0f1f] text-white">
                <div className="hero-content text-center max-w-4xl">
                    <div>
                        <h1 className="text-5xl font-bold mb-6">Solutions for Industries</h1>
                        <p className="text-xl opacity-90">
                            Powerful, Unified Intelligence for Every Industry
                        </p>
                    </div>
                </div>
            </section>

            <section className="relative overflow-hidden">
                <div className="relative w-full min-h-screen overflow-hidden bg-black mx-auto">
                    <video
                        autoPlay
                        loop
                        muted
                        playsInline
                        className="absolute top-0 left-0 w-full h-full object-cover opacity-50"
                    >
                        <source src="/Video_4.mp4" type="video/mp4" />
                        Your browser does not support the video tag.
                    </video>

                    <div className="absolute top-0 left-0 w-full h-64 bg-gradient-to-b from-[#0a0f1f] via-[#0a0f1f]/60 to-transparent pointer-events-none"></div>

                    <div className="absolute bottom-0 left-0 w-full h-64 bg-gradient-to-t from-[#131827] via-gray-black/60 to-transparent pointer-events-none"></div>

                    {/* Content */}
                    <div className="relative max-w-6xl mx-auto pt-35">
                        <div className="text-center text-lg backdrop-blur bg-gray-800/90 shadow-lg card p-2 mx-[15%]">
                            <p>
                                Securiva delivers an all-in-one secure intelligence platform that transforms how organizations
                                operate across every sector. By combining AI Virtual Agents, Cybersecurity, Automation Workflows,
                                Customer Interaction Tools, VPN Secure Access and Data Protection & Compliance into one cohesive
                                ecosystem, Securiva solves industry-specific challenges with unmatched efficiency, reliability,
                                and adaptability.
                            </p>
                            <br />
                            <p>
                                Unlike traditional platforms that offer fragmented tools, Securiva provides an
                                integrated, end-to-end infrastructure where automation, protection, and intelligent communication
                                operate seamlessly together—backed by enterprise-grade security.
                            </p>
                        </div>

                    </div>
                </div>
            </section>

            <section className="flex flex-col gap-6 mx-[15%] my-10">
                <div>
                    <h2 className="subheading">Why Securiva is Different</h2>
                    <p className="subtext">Securiva stands apart through four fundamental value pillars:</p>
                </div>
                <SolutionCard number={"01"} icon={Brain} label={"Unified Intelligence Layer"} description={"Most platforms provide either AI or security—not both. Securiva merges:"} points={
                    [
                        "AI Virtual Agent (voice + text)",
                        "Cybersecurity",
                        "VPN Secure Access",
                        "Automation Workflows",
                        "Customer Interaction Tools",
                        "Data Protection & Compliance"
                    ]
                } footer={"Everything works together in a single architecture."} />
                <SolutionCard number={"02"} icon={Factory} label={"Industry-Adaptive AI"} description={"The AI Virtual Agent automatically adapts to industry rules, vocabulary, workflows, compliance constraints, and customer interaction standards."} />
                <SolutionCard number={"03"} icon={Lock} label={"Zero-Trust Security at the Core"} description={"Instead of adding security as an external layer, Securiva embeds cybersecurity into all interactions, automations, and data flows."} />
                <SolutionCard number={"04"} icon={BadgeCheckIcon} label={"Compliance-Driven by Default"} description={"From healthcare privacy to financial regulations, Securiva ensures all automations and virtual interactions remain fully compliant."} />
            </section>

            <section id="healthcare" className="pb-10">
                <h2 className="subheading">Healthcare</h2>
                <IndustryCard
                    className="mx-[15%]"
                    challenges={[
                        "Patient data protection",
                        "Long wait times",
                        "Manual scheduling",
                        "Sensitive communication",
                        "Compliance with medical standards",
                    ]}
                    solutions={[
                        "AI Virtual Agent for appointment booking, triage, reminders",
                        "Secure patient communication channels",
                        "Automated patient workflows (follow-ups, test notifications)",
                        "Identity verification for patient portals",
                        "Cybersecurity and data governance compliant with industry standards",
                    ]}
                    impact={[
                        "Reduced administrative workload",
                        "Faster patient service",
                        "Stronger protection for medical records",
                        "Automated care coordination",
                    ]}
                />
            </section>

            <section id="fintech" className="pb-10">
                <h2 className="subheading">Finance & Fintech</h2>
                <IndustryCard
                    className="mx-[15%]"
                    challenges={[
                        "High security and fraud-risk environment",
                        "Regulatory compliance",
                        "Customer onboarding and KYC",
                        "Large volumes of inquiries",
                    ]}
                    solutions={[
                        "AI-powered onboarding with secure identity verification",
                        "Automated compliance workflows",
                        "Cybersecurity guardrails for financial transactions",
                        "AI Virtual Agent for client support, loan inquiries, account questions",
                        "Risk detection and alerting"
                    ]}
                    impact={[
                        "Reduced operational risk",
                        "Faster and compliant onboarding",
                        "Higher customer satisfaction",
                        "Scalable financial support automation"
                    ]}
                />
            </section>

            <section id="ecommerce" className="pb-10">
                <h2 className="subheading">E-commerce</h2>
                <IndustryCard
                    className="mx-[15%]"
                    challenges={[
                        "High volume customer interactions",
                        "Order tracking and support",
                        "Fraud detection",
                        "Cart abandonment",
                        "Need for real-time automation",
                    ]}
                    solutions={[
                        "AI Virtual Agent for order status, returns, FAQs",
                        "Cybersecurity protection against fake accounts and online attacks",
                        "Automated cart recovery workflows",
                        "Personalized customer interaction tools",
                        "Compliance and secure payment workflows",
                    ]}
                    impact={[
                        "Increased sales",
                        "Lower support costs",
                        "Higher trust and fraud protection",
                        "Improved customer journey",
                    ]}
                />
            </section>

            <section id="smb" className="pb-10">
                <h2 className="subheading">SMBs</h2>
                <IndustryCard
                    className="mx-[15%]"
                    challenges={[
                        "Limited staff",
                        "Need for automated processes",
                        "Basic security but growing threats",
                        "Customer engagement requirements",
                    ]}
                    solutions={[
                        "All-in-one automation for daily operations",
                        "AI Virtual Agent to handle support and first-level tasks",
                        "Cybersecurity essentials built-in",
                        "Simple workflow automation for admin, sales, HR",
                        "Interaction tools for email, chat, notifications",
                    ]}
                    impact={[
                        "Reduction of manual work",
                        "Professional customer experience",
                        "Improved security posture",
                        "Cost-effective business automation",
                    ]}
                />
            </section>

            <section id="agriculture" className="pb-10">
                <h2 className="subheading">Agriculture</h2>
                <IndustryCard
                    className="mx-[15%]"
                    challenges={[
                        "Supply chain coordination",
                        "Manual paperwork",
                        "Traceability requirements",
                        "Rural communication gaps",
                        "Production and logistics monitoring",
                    ]}
                    solutions={[
                        "AI Virtual Agent for logistics, scheduling, and field requests",
                        "Automated workflows for compliance, reporting, quality control",
                        "Secure data management for farming records",
                        "Customer interaction tools for buyers and suppliers",
                        "Cybersecurity for equipment, IoT sensors, and data",
                    ]}
                    impact={[
                        "Increased efficiency",
                        "Better traceability",
                        "Faster coordination",
                        "Protected agricultural data",
                    ]}
                />
            </section>

            <section id="education" className="pb-10">
                <h2 className="subheading">Education</h2>
                <IndustryCard
                    className="mx-[15%]"
                    challenges={[
                        "High admin workload",
                        "Student services",
                        "Online safety",
                        "Compliance with educational regulations",
                    ]}
                    solutions={[
                        "AI Virtual Agent for school inquiries, onboarding, orientation",
                        "Automated workflows for enrollment, attendance, reporting",
                        "Cybersecurity for student data",
                        "Interaction tools for parents, teachers, students",
                        "Compliance-ready data protection",
                    ]}
                    impact={[
                        "Streamlined academic administration",
                        "Faster communication",
                        "Strong data privacy",
                    ]}
                />
            </section>

            <section id="nonprofit" className="pb-10">
                <h2 className="subheading">Non Profit</h2>
                <IndustryCard
                    className="mx-[15%]"
                    challenges={[
                        "Limited budgets",
                        "High volunteer and donor management load",
                        "Need for transparency",
                        "Sensitive beneficiary data",
                    ]}
                    solutions={[
                        "AI Virtual Agent for donor inquiries, volunteer onboarding",
                        "Automated workflows for reporting, fundraising, communication",
                        "Cybersecurity for sensitive records",
                        "Customer interaction tools for community engagement",
                        "Compliance for grants and audits",
                    ]}
                    impact={[
                        "Lower operational costs",
                        "More time for mission-driven activities",
                        "Stronger community trust",
                    ]}
                />
            </section>

            <section id="government" className="pb-10">
                <h2 className="subheading">Government</h2>
                <IndustryCard
                    className="mx-[15%]"
                    challenges={[
                        "Bureaucracy and slow services",
                        "Identity verification",
                        "Citizen communications",
                        "Compliance and security demands",
                    ]}
                    solutions={[
                        "AI Virtual Agent for public services, forms, FAQs",
                        "Automated workflows for permits, applications, documents",
                        "Cybersecurity and zero-trust protection",
                        "Customer interaction tools for citizens",
                        "Strong compliance and data retention policies",
                    ]}
                    impact={[
                        "Reduced service delays",
                        "Modernized digital services",
                        "Secure citizen data",
                    ]}
                />
            </section>

            <section>
                <h2 className="subheading">Other Industries</h2>
                <div className="rounded-2xl border border-gray-100 bg-gray-50 p-6 dark:border-gray-800 dark:bg-gray-900 mx-[15%]">


                    <p className="text-xl font-medium text-gray-900 dark:text-white mb-4">Securiva is adaptable for:</p>

                    <div className="flex flex-wrap gap-2 mb-5">
                        {[
                            "Logistics",
                            "Real estate",
                            "Transportation",
                            "Hospitality",
                            "Manufacturing",
                            "Professional services",
                        ].map((industry) => (
                            <span
                                className="rounded-lg border border-gray-200 bg-white px-3 py-1 text-lg text-gray-600 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
                            >
                                {industry}
                            </span>
                        ))}
                    </div>

                    <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                        <p className="xl font-medium uppercase tracking-widest text-gray-400 dark:text-gray-600 mb-3">
                            Each integration includes the same foundation
                        </p>
                        <div className="flex flex-wrap gap-2">
                            {[
                                "AI Virtual Agent",
                                "Cybersecurity",
                                "Automation Workflows",
                                "Customer Interaction Tools",
                                "Data Protection & Compliance",
                            ].map((feature) => (
                                <span
                                    key={feature}
                                    className="inline-flex items-center gap-1.5 rounded-lg bg-blue-50 border border-blue-100 px-3 py-1 text-lg text-blue-700 dark:bg-blue-950 dark:border-blue-900 dark:text-blue-300"
                                >
                                    <CheckCircle2 className="h-3 w-3 stroke-blue-500 dark:stroke-blue-400" strokeWidth={2} />
                                    {feature}
                                </span>
                            ))}
                        </div>
                    </div>

                </div>
            </section>

            <section className="px-8 py-16 max-w-4xl mx-auto">
                <h2 className="subheading">The Securiva Advantage</h2>
                <p className="subtext">Regardless of industry, Securiva enables organizations to:</p>
                <SymmetricalChecklist items={
                    [
                        "Automate operations",
                        "Secure data and access",
                        "Improve customer or citizen communication",
                        "Maintain compliance",
                        "Deploy AI Virtual Agents across all touchpoints",
                        "Scale without complexity",
                    ]}
                    size={3.5}
                />
            </section>

        </div>

    );
}