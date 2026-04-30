import { Play, Workflow, Phone, Mail, MessageCircle, File, Network, Brain, Expand, Lock, CircleDollarSign } from "lucide-react";
import { Link } from "react-router-dom";
import CapabilityCard from "../components/CapabilityCard";
import SymmetricalChecklist from "../components/SymmetricalChecklist";
import ReasonCard from "../components/ReasonCard";
import { useTranslation } from "react-i18next";



export default function AgentText({ }) {
    const { t } = useTranslation();
    const reasons = [
        {
            icon: Network,
            label: t("agentText.reasons.items.cross_platform.label"),
            description: t("agentText.reasons.items.cross_platform.description"),
        },
        {
            icon: Brain,
            label: t("agentText.reasons.items.accuracy.label"),
            description: t("agentText.reasons.items.accuracy.description"),
        },
        {
            icon: Expand,
            label: t("agentText.reasons.items.scalable.label"),
            description: t("agentText.reasons.items.scalable.description"),
        },
        {
            icon: Lock,
            label: t("agentText.reasons.items.security.label"),
            description: t("agentText.reasons.items.security.description"),
        },
        {
            icon: CircleDollarSign,
            label: t("agentText.reasons.items.savings.label"),
            description: t("agentText.reasons.items.savings.description"),
        },
    ];
    return (
        <div className="min-h-screen bg-gray-900">

            {/* ---------- HERO ---------- */}
            <section className="hero pt-24 bg-linear-to-br bg-[#0a0f1f] text-white">
                <div className="hero-content text-center">
                    <div>
                        <h1 className="text-5xl font-bold mb-6">
                            {t("agentText.hero.title")}
                        </h1>
                        <p className="text-4xl opacity-90">{t("agentText.hero.subtitle")}</p>

                    </div>
                </div>
            </section>

            <section className="relative overflow-hidden">
                <div className="relative w-full h-[450px] overflow-hidden bg-black mx-auto">
                    <video
                        autoPlay
                        loop
                        muted
                        playsInline
                        className="absolute top-0 left-0 w-full object-cover opacity-40"
                    >
                        <source src="text_agent.mp4" type="video/mp4" />
                        Your browser does not support the video tag.
                    </video>

                    <div className="absolute top-0 left-0 w-full h-64 bg-gradient-to-b from-[#0a0f1f] via-[#0a0f1f]/60 to-transparent pointer-events-none"></div>

                    <div className="absolute bottom-0 left-0 w-full h-64 bg-gradient-to-t from-[#131827] via-gray-black/60 to-transparent pointer-events-none"></div>

                    {/* Content */}
                    <div className="relative max-w-6xl pt-25 mx-auto">
                        <p className="text-center backdrop-blur bg-gray-800/30 shadow-lg card p-10 mx-[15%] text-xl">{t("agentText.overview.description")}</p>
                    </div>
                </div>
            </section>

            <section className="flex flex-col gap-5 mb-5 -mt-15 mx-[15%]">
                <h2 className="z-5 subheading">{t("agentText.capabilities.title")}</h2>
                <CapabilityCard icon={Mail} label={t("agentText.capabilities.items.email.label")} description={t("agentText.capabilities.items.email.description")} />
                <CapabilityCard icon={MessageCircle} label={t("agentText.capabilities.items.chat.label")} description={t("agentText.capabilities.items.chat.description")} />
                <CapabilityCard icon={File} label={t("agentText.capabilities.items.documents.label")} description={t("agentText.capabilities.items.documents.description")} />
                <CapabilityCard icon={Workflow} label={t("agentText.capabilities.items.api.label")} description={t("agentText.capabilities.items.api.description")} />
            </section>

            <section className="gap-5 my-5 mx-[15%]">
                <SymmetricalChecklist heading={t("agentText.advantages.title")} items={t("agentText.advantages.items", { returnObjects: true })} />
            </section>

            <h2 className="subheading">
                {t("agentText.reasons.title")}
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
                <h2 className="text-4xl font-normal mb-3 text-white">
                    {t("agentText.cta.title")}
                </h2>
                <p className="text-2xl font-light mb-10 max-w-xl mx-auto text-gray-400">
                    {t("agentText.cta.description")}
                </p>
                <div className="flex flex-wrap justify-center gap-3">
                    <Link to={"/contact"}>
                        <button className="flex items-center gap-2 rounded-xl bg-red-500 px-6 py-3 text-[14px] font-medium text-white transition-colors hover:bg-red-400">
                            <Play className="h-4 w-4 fill-white stroke-none" />
                            {t("agentText.cta.demo")}
                        </button>
                    </Link>
                    <Link to={"/contact"}>
                        <button onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })} className="flex items-center gap-2 rounded-xl border px-6 py-3 text-[14px] font-medium transition-colors border-gray-700 bg-gray-900 text-white hover:border-gray-600 hover:bg-gray-800">
                            <Workflow className="h-4 w-4 stroke-gray-400" strokeWidth={1.5} />
                            {t("agentText.cta.learn")}
                        </button>
                    </Link>
                    <Link to={"/pricing"}>
                        <button className="flex items-center gap-2 rounded-xl border px-6 py-3 text-[14px] font-medium transition-colors border-gray-700 bg-gray-900 text-white hover:border-gray-600 hover:bg-gray-800">
                            <Phone className="h-4 w-4 stroke-gray-400" strokeWidth={1.5} />
                            {t("agentText.cta.contact")}
                        </button>
                    </Link>
                </div>
            </section>
        </div>
    );
}