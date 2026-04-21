import { Link } from "react-router-dom";
import {
    Mic, ShieldCheck, MessageSquare, Lock,
    Users, Play, CircleDollarSign,
    LayoutDashboard, Zap, Phone
} from "lucide-react";
import { useTheme } from "../context/ThemeContext";
import Checklist from "../components/Checklist";
import { useTranslation } from "react-i18next";

const platforms = [
    {
        number: "01",
        icon: Mic,
        key: "0",
        link: "/agent-voice"
    },
    {
        number: "02",
        icon: ShieldCheck,
        key: "1",
        link: "/cybersecurity"
    },
    {
        number: "03",
        icon: MessageSquare,
        key: "2",
        link: "/agent-text"
    },
    {
        number: "04",
        icon: Lock,
        key: "3",
        link: "/VPN"
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

const PlatformCard = ({ number, icon: Icon, label, tagline, description, capabilities, idealFor, value, link }) => {
    const { theme } = useTheme();
    const { t } = useTranslation();
    return (
        <Link to={link}>
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
                        <p className="text-xl font-medium uppercase tracking-widest text-gray-400 mb-3">{t("platform.capabilities")}</p>
                        <Checklist items={capabilities} size={"3.5"} />
                    </div>

                    {/* Ideal For */}
                    <div className="flex-1 min-w-[140px]">
                        <p className="text-xl font-medium uppercase tracking-widest text-gray-400 mb-3">{t("platform.idealFor")}</p>
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
                        <p className="text-xl font-medium uppercase tracking-widest text-gray-400 mb-3">{t("platform.value")}</p>
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
        </Link>
    );
}

export default function Platform() {
    const { t } = useTranslation();

    const translatedCards = t("platform.cards", { returnObjects: true });

    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900">

            {/* ---------- HERO ---------- */}
            <section className="hero pt-24 bg-linear-to-br bg-[#0a0f1f] text-white">
                <div className="hero-content text-center max-w-4xl">
                    <div>
                        <h1 className="text-5xl font-bold mb-6">
                            {t("platform.hero.title")}
                        </h1>
                        <p className="text-xl opacity-90">
                            {t("platform.hero.description")}
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
                        <source src="Video_3.mp4" type="video/mp4" />
                        Your browser does not support the video tag.
                    </video>

                    <div className="absolute top-0 left-0 w-full h-64 bg-gradient-to-b from-[#0a0f1f] via-[#0a0f1f]/60 to-transparent pointer-events-none"></div>

                    <div className="absolute bottom-0 left-0 w-full h-64 bg-gradient-to-t from-[#131827] via-gray-black/60 to-transparent pointer-events-none"></div>

                    <div className="relative max-w-6xl mx-auto pt-10">

                        <h2 className="subheading">
                            {t("platform.overview.title")}
                        </h2>

                        <p className="text-center backdrop-blur bg-gray-800/30 shadow-lg card p-10 mx-[15%] text-xl">
                            {t("platform.overview.description")}
                        </p>

                    </div>
                </div>
            </section>

            <section className="px-8 pb-16 mx-[15%]">

                <h2 className="text-center text-3xl font-normal text-gray-900 mb-3 dark:text-white">
                    {t("platform.components.title")}
                </h2>
                {/* Platform Cards */}
                <div className="flex flex-col gap-4 mb-8">
                    {platforms.map((platform, index) => {
                        const content = translatedCards[index];
                        return (
                            <PlatformCard
                                key={platform.number}
                                number={platform.number}
                                icon={platform.icon}
                                link={platform.link}
                                label={content.label}
                                tagline={content.tagline}
                                description={content.description}
                                capabilities={content.capabilities}
                                idealFor={content.idealFor}
                                value={content.value}
                            />
                        );
                    })}
                </div>

                {/* Unified Architecture Note */}
                <div className="rounded-2xl border border-gray-100 bg-gray-50 p-6 mb-4 dark:border-gray-800 dark:bg-gray-900">
                    <div className="flex gap-3 mb-4">
                        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-950">
                            <LayoutDashboard className="h-4 w-4 stroke-blue-600 dark:stroke-blue-400" strokeWidth={1.5} />
                        </div>
                        <div>
                            <h3 className="text-xl font-medium text-gray-900 dark:text-white mb-0.5">
                                {t("platform.unifiedArchitecture.title")}
                            </h3>

                            <p className="text-[19px] text-gray-500 dark:text-gray-400 leading-relaxed">
                                {t("platform.unifiedArchitecture.description")}
                            </p>
                        </div>
                    </div>
                    <Checklist
                        className="pl-12"
                        size="3.5"
                        items={t("platform.unifiedArchitecture.points", { returnObjects: true })}
                    />
                </div>

                {/* Why Organizations Choose Securiva */}
                <div className="rounded-2xl border border-blue-100 bg-blue-50 p-6 dark:border-blue-900 dark:bg-blue-950">
                    <h3 className="text-xl font-medium text-gray-900 dark:text-white mb-1">
                        {t("platform.whyChoose.title")}
                    </h3>

                    <p className="text-[19px] text-gray-500 dark:text-blue-300 mb-4">
                        {t("platform.whyChoose.subtitle")}
                    </p>

                    <Checklist
                        items={t("platform.whyChoose.items", { returnObjects: true })}
                        size={"3.5"}
                    />
                </div>

            </section>

            {/* Call to Action */}
            <section className="px-8 py-16 text-center">
                <h2 className="text-4xl font-normal text-gray-900 mb-3 dark:text-white">
                    {t("platform.cta.title")}
                </h2>

                <p className="text-2xl font-light text-gray-500 mb-10 max-w-xl mx-auto dark:text-gray-400">
                    {t("platform.cta.subtitle")}
                </p>
                <div className="flex flex-wrap justify-center gap-3">
                    <Link to={"/contact"}>
                        <button className="flex items-center gap-2 rounded-xl bg-red-500 px-6 py-3 text-[14px] font-medium text-white transition-colors hover:bg-red-400">
                            <Play className="h-4 w-4 fill-white stroke-none" />
                            {t("platform.cta.requestDemo")}
                        </button>
                    </Link>
                    <Link to={"/contact"}>
                        <button className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-6 py-3 text-[14px] font-medium text-gray-800 transition-colors hover:border-gray-300 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:hover:border-gray-600 dark:hover:bg-gray-800">
                            <Phone className="h-4 w-4 stroke-gray-500 dark:stroke-gray-400" strokeWidth={1.5} />
                            {t("platform.cta.contactSales")}
                        </button>
                    </Link>
                    <Link to={"/pricing"}>
                        <button className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-6 py-3 text-[14px] font-medium text-gray-800 transition-colors hover:border-gray-300 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:hover:border-gray-600 dark:hover:bg-gray-800">
                            <CircleDollarSign className="h-4 w-4 stroke-gray-500 dark:stroke-gray-400" strokeWidth={1.5} />
                            {t("platform.cta.pricing")}
                        </button>
                    </Link>
                </div>
            </section>
        </div>
    );
}