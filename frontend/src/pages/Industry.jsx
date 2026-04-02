import { BadgeCheckIcon, Brain, Factory, Lock } from "lucide-react";
import SolutionCard from "../components/SolutionCard";
import { useTheme } from "../context/ThemeContext";
export default function Industry() {
    const { theme } = useTheme();
    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900">

            {/* ---------- HERO ---------- */}
            <section className="hero py-24 bg-linear-to-br from-blue-900 to-black text-white">
                <div className="hero-content text-center max-w-4xl">
                    <div>
                        <h1 className="text-5xl font-bold mb-6">Solutions for Industries</h1>
                        <p className="text-xl opacity-90">
                            Powerful, Unified Intelligence for Every Industry
                        </p>
                    </div>
                </div>
            </section>

            <section className="pt-10 mb-6 text-center">
                <p className="subtext">
                    Securiva delivers an all-in-one secure intelligence platform that transforms how organizations 
                    operate across every sector. By combining AI Virtual Agents, Cybersecurity, Automation Workflows, 
                    Customer Interaction Tools, VPN Secure Access and Data Protection & Compliance into one cohesive 
                    ecosystem, Securiva solves industry-specific challenges with unmatched efficiency, reliability, 
                    and adaptability.
                </p>
                <p class="subtext">
                    Unlike traditional platforms that offer fragmented tools, Securiva provides an 
                    integrated, end-to-end infrastructure where automation, protection, and intelligent communication 
                    operate seamlessly together—backed by enterprise-grade security.
                </p>
                <div class="border-t border-gray-100 mb-8 dark:border-gray-800" />
            </section>

            <section id="healthcare" className="flex flex-col gap-6 mx-[15%] my-10">
                <div>
                    <h2 class="subheading">Why Securiva is Different</h2>
                    <p class="subtext">Securiva stands apart through four fundamental value pillars:</p>
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
                } footer={"Everything works together in a single architecture."}/>
                <SolutionCard number={"02"} icon={Factory} label={"Industry-Adaptive AI"} description={"The AI Virtual Agent automatically adapts to industry rules, vocabulary, workflows, compliance constraints, and customer interaction standards."}/>
                <SolutionCard number={"03"} icon={Lock} label={"Zero-Trust Security at the Core"} description={"Instead of adding security as an external layer, Securiva embeds cybersecurity into all interactions, automations, and data flows."} />
                <SolutionCard number={"04"} icon={BadgeCheckIcon} label={"Compliance-Driven by Default"} description={"From healthcare privacy to financial regulations, Securiva ensures all automations and virtual interactions remain fully compliant."} />
            </section>

            <section id="healthcare" className="section-min-height">
                <h2 class="subheading">Healthcare</h2>
            </section>

            <section id="fintech" className="section-min-height">
                <h2>Finance & Fintech</h2>
            </section>

            <section id="ecommerce" className="section-min-height">
                <h2 class="subheading">E-commerce</h2>
            </section>

            <section id="smb" className="section-min-height">
                <h2 class="subheading">SMBs</h2>
            </section>

            <section id="agriculture" className="section-min-height">
                <h2 class="subheading">Agriculture</h2>
            </section>

            <section id="technology" className="section-min-height">
                <h2 class="subheading">Technology</h2>
            </section>

            <section id="nonprofit" className="section-min-height">
                <h2 class="subheading">Non Profit</h2>
            </section>

            <section id="government" className="section-min-height">
                <h2 class="subheading">Government</h2>
            </section>

        </div>
    );
}