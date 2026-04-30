import {
    ArrowLeftRight,
    BrainCircuit,
    ClipboardList,
    GlobeLock,
    HouseWifi,
    KeyRound,
    Lock,
    MessageSquare,
    Mic,
    Network,
    PocketKnife,
    Share2,
    ShieldAlert,
    ShieldCheck,
    Trophy,
    Users,
    Workflow,
    WorkflowIcon,
    X,
    Zap
} from "lucide-react";

import SolutionCard from "../components/SolutionCard";
import CapabilityCard from "../components/CapabilityCard";
import SymmetricalChecklist from "../components/SymmetricalChecklist";
import Checklist from "../components/Checklist";
import ReasonCard from "../components/ReasonCard";
import { useTranslation } from "react-i18next";

const reasons = [
    {
        icon: Users,
        labelKey: "vpn.reasons.remoteTeams.label",
        descriptionKey: "vpn.reasons.remoteTeams.description",
    },
    {
        icon: ClipboardList,
        labelKey: "vpn.reasons.regulated.label",
        descriptionKey: "vpn.reasons.regulated.description"
    },
    {
        icon: BrainCircuit,
        labelKey: "vpn.reasons.aiSecurity.label",
        descriptionKey: "vpn.reasons.aiSecurity.description"
    },
    {
        icon: ArrowLeftRight,
        labelKey: "vpn.reasons.crossBorder.label",
        descriptionKey: "vpn.reasons.crossBorder.description"
    },
    {
        icon: WorkflowIcon,
        labelKey: "vpn.reasons.apiWorkflows.label",
        descriptionKey: "vpn.reasons.apiWorkflows.description"
    }
];

export default function VPN() {
    const { t } = useTranslation();

    const integrationCards = t("vpn.integrationCards", { returnObjects: true });
    const featureItems = t("vpn.features.items", { returnObjects: true });
    const valueItems = t("vpn.value.items", { returnObjects: true });
    const finalItems = t("vpn.final.items", { returnObjects: true });

    const featureIcons = [Workflow, ShieldAlert, Share2, ShieldCheck, KeyRound];
    const valueIcons = [PocketKnife, HouseWifi, Trophy];

    const iconMap = {
        "AI Agent Voice": Mic,
        "Agent vocal IA": Mic,

        "Text Agent": MessageSquare,
        "Agent textuel": MessageSquare,

        "Cybersecurity Engine": Lock,
        "Moteur de cybersécurité": Lock,

        "Automation Workflows": Zap,
        "Flux d’automatisation": Zap,

        "System Integrations (Gmail, WhatsApp, Salesforce, Banking APIs, Cloud Platforms, OpenAI, etc.)": Network,
        "Intégrations système (Gmail, WhatsApp, Salesforce, API bancaires, plateformes cloud, OpenAI, etc.)": Network
    };

    

    return (
        <div className="min-h-screen bg-gray-900">

            {/* ---------- HERO ---------- */}
            <section className="hero pt-24 bg-linear-to-br bg-[#0a0f1f] text-white">
                <div className="hero-content text-center max-w-4xl">
                    <div>
                        <h1 className="text-5xl font-bold mb-6">
                            {t("vpn.hero.title")}
                        </h1>
                        <p className="text-xl opacity-90">
                            {t("vpn.hero.subtitle")}
                        </p>
                    </div>
                </div>
            </section>

            {/* ---------- INTRO ---------- */}
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
                    </video>

                    <div className="absolute top-0 left-0 w-full h-64 bg-gradient-to-b from-[#0a0f1f] via-[#0a0f1f]/60 to-transparent pointer-events-none"></div>
                    <div className="absolute bottom-0 left-0 w-full h-64 bg-gradient-to-t from-[#131827] via-gray-black/60 to-transparent pointer-events-none"></div>

                    <div className="relative max-w-6xl mx-auto pt-10">
                        <h2 className="subheading">
                            {t("vpn.intro.title")}
                        </h2>

                        <p className="text-center card p-2 mx-[15%] backdrop-blur bg-gray-800/50 shadow-lg text-xl">
                            {t("vpn.intro.description")}
                        </p>
                    </div>
                </div>
            </section>

            {/* ---------- INTEGRATION ---------- */}
            <section className="relative overflow-hidden px-8 pb-6 -mt-20">
                <h2 className="subheading">
                    {t("vpn.integration.title")}
                </h2>

                <p className="text-xl font-light mb-8 text-center text-gray-400 mx-[15%]">
                    {t("vpn.integration.subtitle")}
                </p>

                <div className="flex flex-wrap gap-3 mb-6 mx-[15%]">
                    {integrationCards.map((card) => (
                        <CapabilityCard
                            className="sm:min-w-[35%] min-w-[70%]"
                            key={card.label}
                            icon={iconMap[card.label] || Mic}
                            label={card.label}
                            description={card.description}
                        />
                    ))}
                </div>

                <p className="text-xl font-light text-center text-gray-400 mx-[15%]">
                    {t("vpn.integration.footer")}
                </p>
            </section>

            {/* ---------- FEATURES ---------- */}
            <section className="flex flex-col gap-5 py-5 mx-[15%]">
                <h2 className="subheading">
                    {t("vpn.features.title")}
                </h2>

                {featureItems.map((item, i) => (
                    <SolutionCard
                        key={item.label}
                        number={`0${i + 1}`}
                        icon={featureIcons[i]}
                        label={item.label}
                        description={item.description}
                        points={item.points}
                        footer={item.footer}
                    />
                ))}
            </section>

            {/* ---------- VALUE ---------- */}
            <section className="flex flex-col gap-5 py-5 mx-[15%]">
                <h2 className="subheading">
                    {t("vpn.value.title")}
                </h2>

                {valueItems.map((item, i) => (
                    <SolutionCard
                        key={item.label}
                        icon={valueIcons[i]}
                        label={item.label}
                        description={item.description || item.intro}
                        points={item.points}
                        footer={item.footer}
                        content={
                            item.badItems ? (
                                <div>
                                    <ul className="flex flex-col gap-1.5 pb-2">
                                        {item.badItems.map((bad) => (
                                            <li key={bad} className="flex items-start gap-2 text-lg text-gray-300">
                                                <X className="mt-2 h-3.5 w-3.5 shrink-0 stroke-blue-400" />
                                                {bad}
                                            </li>
                                        ))}
                                    </ul>
                                    <p className="text-lg mb-3 leading-relaxed text-gray-400">
                                        {item.closing}
                                    </p>
                                    <Checklist
                                        items={item.checklist || []}
                                        size={"3.5"}
                                    />
                                </div>
                            ) : null
                        }
                    />
                ))}
            </section>

            {/* ---------- USE CASES ---------- */}
            <section className="flex flex-col gap-5 py-5 mx-[15%]">
                <h2 className="subheading">
                    {t("vpn.useCases.title")}
                </h2>

                <div className="flex flex-wrap justify-center gap-3 mb-10">
                    {reasons.map((reason) => (
                        <ReasonCard
                            key={reason.labelKey}
                            icon={reason.icon}
                            label={t(reason.labelKey)}
                            description={t(reason.descriptionKey)}
                        />
                    ))}
                </div>
            </section>

            {/* ---------- FINAL ---------- */}
            <section className="flex flex-col gap-5 py-5 mx-[15%]">
                <h2 className="subheading">
                    {t("vpn.final.title")}
                </h2>

                <CapabilityCard
                    icon={GlobeLock}
                    label={t("vpn.final.description")}
                    content={
                        <SymmetricalChecklist items={finalItems} />
                    }
                />
            </section>
        </div>
    );
}