import CapabilityCard from "../components/CapabilityCard";
import { AudioLines, AudioWaveform, BadgeCheck, Languages, NotepadTextDashed, Send, Videotape } from "lucide-react";
import SymmetricalChecklist from "../components/SymmetricalChecklist";

export default function AgentVoice({ }) {
    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900">

            {/* ---------- HERO ---------- */}
            <section className="hero pt-24 bg-linear-to-br bg-[#0a0f1f] text-white">
                <div className="hero-content text-center max-w-4xl">
                    <div>
                        <h1 className="text-5xl font-bold mb-6">AI Agent Voice: Intelligent Voice-to-Action Engine </h1>
                        <p className="text-xl opacity-90">
                            AI Voice is SecuriVA’s advanced vocal intelligence module that converts speech into smart text, contextualized messages, translations, and automated actions.
                            Users simply speak, and SecuriVA understands, reformulates, translates, analyzes, and executes.
                        </p>
                    </div>
                </div>
            </section>

            <section className="relative overflow-hidden">
                <div className="relative w-full h-[500px] overflow-hidden bg-black mx-auto">
                    <video
                        autoPlay
                        loop
                        muted
                        playsInline
                        className="absolute top-0 left-0 w-full h-[70%] object-cover opacity-40"
                    >
                        <source src="Voice_AI_agent.mp4" type="video/mp4" />
                        Your browser does not support the video tag.
                    </video>

                    <div className="absolute top-0 left-0 w-full h-64 bg-gradient-to-b from-[#0a0f1f] via-[#0a0f1f]/60 to-transparent pointer-events-none"></div>

                    <div className="absolute bottom-0 left-0 w-full h-64 bg-gradient-to-t from-[#131827] via-gray-black/60 to-transparent pointer-events-none"></div>

                    {/* Content */}
                    <div className="relative max-w-6xl mx-auto pt-10">

                        <h2 className="subheading">
                            A Unified Intelligent Platform for Secure, Automated, AI-Driven Operations
                        </h2>
                        <p className="text-center backdrop-blur bg-gray-800/30 shadow-lg card p-10 mx-[15%] text-xl">Our platform is designed to support organizations of all sizes—across all industries—seeking to modernize their operations, protect their data, and elevate customer engagement.</p>
                    </div>
                </div>
            </section>

            <section className="flex flex-col gap-5 py-5 mx-[15%]">
                <CapabilityCard icon={AudioLines} label={"High-Accuracy Voice-to-Text"} description={"Instant conversion of speech into structured text, regardless of speed, accent, or language."} />
                <CapabilityCard icon={NotepadTextDashed} label={"Intelligent Rewriting by Tone"} description={"From the dictated text, the agent generates optimized versions in different tones"} />
                <CapabilityCard icon={Languages} label={"Automatic Multilingual Translation"} description={"Seamless translation into any language: EN, FR, ES, AR, Lingala, Swahili, Mandarin, Portuguese, etc."} />
                <CapabilityCard icon={Send} label={"Automated Sending Across Channels"} description={"After user validation, AI Voice can send the message via:"} content=
                    {
                        <SymmetricalChecklist items={["Email",
                            "SMS / Text",
                            "WhatsApp",
                            "Messenger",
                            "Slack",
                            "Internal CRM",
                            "Custom APIs"
                        ]} />
                    } />
                <CapabilityCard icon={Videotape} label={"Meeting Listening, Recording & Smart Reporting"} description={"AI Voice becomes an intelligent meeting assistant, capable of:"} content=
                    {
                        <div className="flex flex-col gap-5">
                            <div className="rounded-2xl p-6">
                                <h3 className="text-xl font-medium text-gray-900 dark:text-white mb-1">Listening to Live Meetings</h3>
                                <p className="text-[19px] text-gray-500 dark:text-blue-300 mb-4">The agent can join or capture:</p>
                                <SymmetricalChecklist items={[
                                    "Virtual meetings (Zoom, Teams, Google Meet, etc.)",
                                    "In-person meetings (via microphone)",
                                    "Conference calls",
                                    "Business calls",
                                ]} size={"3.5"} />
                            </div>
                            <div className="border border-gray-700 mx-[15%]" />
                            <div className="rounded-2xl p-6">
                                <h3 className="text-xl font-medium text-gray-900 dark:text-white mb-1">Recording and Analyzing Audio</h3>
                                <p className="text-[19px] text-gray-500 dark:text-blue-300 mb-4">The agent:</p>
                                <SymmetricalChecklist items={[
                                    "Records continuous audio",
                                    "Detects speakers",
                                    "Automatically segments discussion topics",
                                ]} size={"3.5"} />
                            </div>

                            <div className="border border-gray-700 mx-[15%]" />

                            <div className="rounded-2xl p-6">
                                <h3 className="text-xl font-medium text-gray-900 dark:text-white mb-1">Generating Detailed Reports</h3>
                                <p className="text-[19px] text-gray-500 dark:text-blue-300 mb-4">At the end of the meeting, SecuriVA automatically produces:</p>

                                <p className="text-[15px] font-medium text-gray-700 dark:text-blue-200 mb-2">Executive Summary</p>
                                <SymmetricalChecklist items={[
                                    "Objectives",
                                    "Key decisions",
                                    "Action items",
                                    "Responsible persons",
                                    "Deadlines",
                                ]} size={"3.5"} />

                                <p className="text-[15px] font-medium text-gray-700 dark:text-blue-200 mt-4 mb-2">Full Report</p>
                                <SymmetricalChecklist items={[
                                    "Complete transcript",
                                    "Summary per speaker",
                                    "Summary per topic",
                                    "Risk alerts, opportunities, and insights",
                                    "Tone and coherence analysis",
                                ]} size={"3.5"} />
                            </div>

                            <div className="border border-gray-700 mx-[15%]" />

                            <div className="rounded-2xl p-6">
                                <h3 className="text-xl font-medium text-gray-900 dark:text-white mb-1">Export in Multiple Formats</h3>
                                <p className="text-[19px] text-gray-500 dark:text-blue-300 mb-4">Users can download the report in:</p>
                                <SymmetricalChecklist items={[
                                    "PDF",
                                    "Word (DOCX)",
                                    "Text (TXT)",
                                    "Markdown",
                                    "CSV (task lists)",
                                ]} size={"3.5"} />
                            </div>

                            <div className="border border-gray-700 mx-[15%]" />

                            <div className="rounded-2xl p-6">
                                <h3 className="text-xl font-medium text-gray-900 dark:text-white mb-1">Automatic Distribution</h3>
                                <p className="text-[19px] text-gray-500 dark:text-blue-300 mb-4">Through voice command, SecuriVA can:</p>
                                <SymmetricalChecklist items={[
                                    "Send the report by email",
                                    "Share it via WhatsApp / Slack",
                                    "Archive it in cloud storage",
                                    "Forward it to a team or partner",
                                ]} size={"3.5"} />
                            </div>
                        </div>
                    } />


                <CapabilityCard icon={AudioWaveform} label={"Advanced Voice Commands"} description={"Examples:"} content=
                    {
                        <div className="flex flex-wrap gap-2">
                            {[
                                "“SecuriVA, listen and record the meeting.”",
                                "“Generate a professional report and send it to the team.”",
                                "“Summarize the conversation in a formal tone.”",
                                "“Translate the report to Spanish and export it as PDF.”",
                            ].map((feature, index) => (
                                <span
                                    key={feature}
                                    className="inline-flex items-center gap-1.5 rounded-lg bg-blue-50 border border-blue-100 px-3 py-1 text-lg text-blue-700 dark:bg-blue-950 dark:border-blue-900 dark:text-blue-300"
                                >
                                    <p className="text-lg stroke-blue-500 dark:stroke-blue-400">{index+1}.{feature}</p>
                                </span>
                            ))}
                        </div>
                    } />
                <CapabilityCard icon={BadgeCheck} label={"Compliance & Smart History"} content=
                    {
                        <div className="flex flex-col gap-5">
                            <div className="rounded-2xl p-6">
                                <h3 className="text-xl font-medium text-gray-900 dark:text-white mb-1">The agent saves:</h3>
                                <SymmetricalChecklist items={[
                                    "Authorized recordings",
                                    "Generated reports",
                                    "Sent messages"
                                ]} size={"3.5"} />
                            </div>
                            <div className="border border-gray-700 mx-[15%]" />
                            <div className="rounded-2xl p-6">
                                <h3 className="text-xl font-medium text-gray-900 dark:text-white mb-1">With protections:</h3>
                                <SymmetricalChecklist items={[
                                    "GDPR / PIPEDA compliance",
                                    "Access control",
                                    "Encrypted audio storage"
                                ]} size={"3.5"} />
                            </div>
                        </div>
                    } />
            </section>
        </div>
    );
}