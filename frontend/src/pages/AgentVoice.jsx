import CapabilityCard from "../components/CapabilityCard";
import { AudioLines, AudioWaveform, BadgeCheck, Languages, NotepadTextDashed, Send, Videotape } from "lucide-react";
import Checklist from "../components/Checklist";
import SymmetricalChecklist from "../components/SymmetricalChecklist";

export default function AgentVoice({ }) {
    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900">

            {/* ---------- HERO ---------- */}
            <section className="hero py-24 bg-linear-to-br from-blue-900 to-black text-white">
                <div className="hero-content text-center max-w-4xl">
                    <div>
                        <h1 className="text-5xl font-bold mb-6">AI Agent Voice : Intelligent Voice-to-Action Engine </h1>
                        <p className="text-xl opacity-90">
                            AI Voice is SecuriVA’s advanced vocal intelligence module that converts speech into smart text, contextualized messages, translations, and automated actions.
                            Users simply speak, and SecuriVA understands, reformulates, translates, analyzes, and executes.
                        </p>
                    </div>
                </div>
            </section>

            <section className="flex flex-col gap-5 my-5 mx-[15%]">
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
                        <div className="flex flex-col items-center gap-5">
                            <div className="rounded-2xl border border-blue-100 bg-blue-50 px-8 py-6 text-center dark:border-blue-900 dark:bg-blue-950">
                                <p className="text-[15px] font-light italic text-blue-700 dark:text-blue-300">
                                    “SecuriVA, listen and record the meeting.”
                                </p>
                            </div>

                            <div className="rounded-2xl border border-blue-100 bg-blue-50 px-8 py-6 text-center dark:border-blue-900 dark:bg-blue-950">
                                <p className="text-[15px] font-light italic text-blue-700 dark:text-blue-300">
                                    “Generate a professional report and send it to the team.”
                                </p>
                            </div>

                            <div className="rounded-2xl border border-blue-100 bg-blue-50 px-8 py-6 text-center dark:border-blue-900 dark:bg-blue-950">
                                <p className="text-[15px] font-light italic text-blue-700 dark:text-blue-300">
                                    “Summarize the conversation in a formal tone.”
                                </p>
                            </div>

                            <div className="rounded-2xl border border-blue-100 bg-blue-50 px-8 py-6 text-center dark:border-blue-900 dark:bg-blue-950">
                                <p className="text-[15px] font-light italic text-blue-700 dark:text-blue-300">
                                    “Translate the report to Spanish and export it as PDF.”
                                </p>
                            </div>
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