import CapabilityCard from "../components/CapabilityCard";
import { AudioLines, AudioWaveform, BadgeCheck, Languages, NotepadTextDashed, Send, Videotape } from "lucide-react";
import SymmetricalChecklist from "../components/SymmetricalChecklist";
import { useTranslation } from "react-i18next";

export default function AgentVoice({ }) {
    const { t } = useTranslation();
    return (
        <div className="min-h-screen bg-gray-900">

            {/* ---------- HERO ---------- */}
            <section className="hero pt-24 bg-linear-to-br bg-[#0a0f1f] text-white">
                <div className="hero-content text-center max-w-4xl">
                    <div>
                        <h1 className="text-5xl font-bold mb-6">{t("agentVoice.hero.title")} </h1>
                        <p className="text-xl opacity-90">
                            {t("agentVoice.hero.description")}
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
                            {t("agentVoice.overview.title")}
                        </h2>
                        <p className="text-center backdrop-blur bg-gray-800/30 shadow-lg card p-10 mx-[15%] text-xl">{t("agentVoice.overview.description")}</p>
                    </div>
                </div>
            </section>

            <section className="flex flex-col gap-5 py-5 mx-[15%]">
                <CapabilityCard icon={AudioLines} label={t("agentVoice.capabilities.voiceToText.label")} description={t("agentVoice.capabilities.voiceToText.description")} />
                <CapabilityCard icon={NotepadTextDashed} label={t("agentVoice.capabilities.rewriting.label")} description={t("agentVoice.capabilities.rewriting.description")} />
                <CapabilityCard icon={Languages} label={t("agentVoice.capabilities.translation.label")} description={t("agentVoice.capabilities.translation.description")} />
                <CapabilityCard icon={Send} label={t("agentVoice.capabilities.sending.label")} description={t("agentVoice.capabilities.sending.description")} content=
                    {
                        <SymmetricalChecklist items={t("agentVoice.capabilities.sending.items", { returnObjects: true })} />
                    } />
                <CapabilityCard
                    icon={Videotape}
                    label={t("agentVoice.capabilities.meetings.label")}
                    description={t("agentVoice.capabilities.meetings.description")}
                    content={
                        <div className="flex flex-col gap-5">

                            {/* Listening */}
                            <div className="rounded-2xl p-6">
                                <h3 className="text-xl font-medium mb-1">
                                    {t("agentVoice.capabilities.meetings.listening.title")}
                                </h3>
                                <p className="mb-4">
                                    {t("agentVoice.capabilities.meetings.listening.subtitle")}
                                </p>
                                <SymmetricalChecklist
                                    items={t("agentVoice.capabilities.meetings.listening.items", { returnObjects: true })}
                                    size={"3.5"}
                                />
                            </div>

                            <div className="border mx-[15%]" />

                            {/* Recording */}
                            <div className="rounded-2xl p-6">
                                <h3 className="text-xl font-medium mb-1">
                                    {t("agentVoice.capabilities.meetings.recording.title")}
                                </h3>
                                <p className="mb-4">
                                    {t("agentVoice.capabilities.meetings.recording.subtitle")}
                                </p>
                                <SymmetricalChecklist
                                    items={t("agentVoice.capabilities.meetings.recording.items", { returnObjects: true })}
                                    size={"3.5"}
                                />
                            </div>

                            <div className="border mx-[15%]" />

                            {/* Reports */}
                            <div className="rounded-2xl p-6">
                                <h3 className="text-xl font-medium mb-1">
                                    {t("agentVoice.capabilities.meetings.reports.title")}
                                </h3>
                                <p className="mb-4">
                                    {t("agentVoice.capabilities.meetings.reports.subtitle")}
                                </p>

                                <p className="mb-2">
                                    {t("agentVoice.capabilities.meetings.reports.executive.title")}
                                </p>
                                <SymmetricalChecklist
                                    items={t("agentVoice.capabilities.meetings.reports.executive.items", { returnObjects: true })}
                                    size={"3.5"}
                                />

                                <p className="mt-4 mb-2">
                                    {t("agentVoice.capabilities.meetings.reports.full.title")}
                                </p>
                                <SymmetricalChecklist
                                    items={t("agentVoice.capabilities.meetings.reports.full.items", { returnObjects: true })}
                                    size={"3.5"}
                                />
                            </div>

                            <div className="border mx-[15%]" />

                            {/* Export */}
                            <div className="rounded-2xl p-6">
                                <h3 className="text-xl font-medium mb-1">
                                    {t("agentVoice.capabilities.meetings.export.title")}
                                </h3>
                                <p className="mb-4">
                                    {t("agentVoice.capabilities.meetings.export.subtitle")}
                                </p>
                                <SymmetricalChecklist
                                    items={t("agentVoice.capabilities.meetings.export.items", { returnObjects: true })}
                                    size={"3.5"}
                                />
                            </div>

                            <div className="border mx-[15%]" />

                            {/* Distribution */}
                            <div className="rounded-2xl p-6">
                                <h3 className="text-xl font-medium mb-1">
                                    {t("agentVoice.capabilities.meetings.distribution.title")}
                                </h3>
                                <p className="mb-4">
                                    {t("agentVoice.capabilities.meetings.distribution.subtitle")}
                                </p>
                                <SymmetricalChecklist
                                    items={t("agentVoice.capabilities.meetings.distribution.items", { returnObjects: true })}
                                    size={"3.5"}
                                />
                            </div>

                        </div>
                    }
                />


                <CapabilityCard
                    icon={AudioWaveform}
                    label={t("agentVoice.capabilities.commands.label")}
                    description={t("agentVoice.capabilities.commands.description")}
                    content={
                        <div className="flex flex-wrap gap-2">
                            {t("agentVoice.capabilities.commands.items", { returnObjects: true }).map((item, index) => (
                                <span
                                    key={item}
                                    className="inline-flex items-center gap-1.5 rounded-lg border px-3 py-1 text-lg bg-blue-950 border-blue-900 text-blue-300"
                                >
                                    <p className="text-lg">
                                        {index + 1}. {item}
                                    </p>
                                </span>
                            ))}
                        </div>
                    }
                />
                <CapabilityCard
                    icon={BadgeCheck}
                    label={t("agentVoice.capabilities.compliance.label")}
                    content={
                        <div className="flex flex-col gap-5">

                            {/* Saves */}
                            <div className="rounded-2xl p-6">
                                <h3 className="text-xl font-medium mb-1">
                                    {t("agentVoice.capabilities.compliance.saves.title")}
                                </h3>
                                <SymmetricalChecklist
                                    items={t("agentVoice.capabilities.compliance.saves.items", { returnObjects: true })}
                                    size={"3.5"}
                                />
                            </div>

                            <div className="border mx-[15%]" />

                            {/* Protection */}
                            <div className="rounded-2xl p-6">
                                <h3 className="text-xl font-medium mb-1">
                                    {t("agentVoice.capabilities.compliance.protection.title")}
                                </h3>
                                <SymmetricalChecklist
                                    items={t("agentVoice.capabilities.compliance.protection.items", { returnObjects: true })}
                                    size={"3.5"}
                                />
                            </div>

                        </div>
                    }
                />
            </section>
        </div>
    );
}