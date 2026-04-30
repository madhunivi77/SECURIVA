import { BadgeCheckIcon, Brain, CheckCircle2, Factory, Lock } from "lucide-react";
import SolutionCard from "../components/SolutionCard";
import { useTheme } from "../context/ThemeContext";
import IndustryCard from "../components/IndustryCard";
import SymmetricalChecklist from "../components/SymmetricalChecklist";
import { useTranslation } from "react-i18next";

export default function Industry() {
    const { theme } = useTheme();
    const { t } = useTranslation();

    return (
        <div className="min-h-screen bg-gray-900">

            {/* ---------- HERO ---------- */}
            <section className="hero py-24 bg-linear-to-br bg-[#0a0f1f] text-white">
                <div className="hero-content text-center max-w-4xl">
                    <div>
                        <h1 className="text-5xl font-bold mb-6">
                            {t("industry.hero.title")}
                        </h1>
                        <p className="text-xl opacity-90">
                            {t("industry.hero.subtitle")}
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
                                {t("industry.intro.paragraph1")}
                            </p>
                            <br />
                            <p>
                                {t("industry.intro.paragraph2")}
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            <section className="flex flex-col gap-6 mx-[15%] my-10">
                <div>
                    <h2 className="subheading">{t("industry.why.title")}</h2>
                    <p className="subtext">{t("industry.why.subtitle")}</p>
                </div>

                <SolutionCard
                    number={"01"}
                    icon={Brain}
                    label={t("industry.why.cards.unified.title")}
                    description={t("industry.why.cards.unified.description")}
                    points={t("industry.why.cards.unified.points", { returnObjects: true })}
                    footer={t("industry.why.cards.unified.footer")}
                />

                <SolutionCard
                    number={"02"}
                    icon={Factory}
                    label={t("industry.why.cards.adaptive.title")}
                    description={t("industry.why.cards.adaptive.description")}
                />

                <SolutionCard
                    number={"03"}
                    icon={Lock}
                    label={t("industry.why.cards.zeroTrust.title")}
                    description={t("industry.why.cards.zeroTrust.description")}
                />

                <SolutionCard
                    number={"04"}
                    icon={BadgeCheckIcon}
                    label={t("industry.why.cards.compliance.title")}
                    description={t("industry.why.cards.compliance.description")}
                />
            </section>

            <section id="healthcare" className="pb-10">
                <h2 className="subheading">{t("industry.industries.healthcare.title")}</h2>
                <IndustryCard
                    className="mx-[15%]"
                    challenges={t("industry.industries.healthcare.challenges", { returnObjects: true })}
                    solutions={t("industry.industries.healthcare.solutions", { returnObjects: true })}
                    impact={t("industry.industries.healthcare.impact", { returnObjects: true })}
                />
            </section>

            <section id="fintech" className="pb-10">
                <h2 className="subheading">{t("industry.industries.fintech.title")}</h2>
                <IndustryCard
                    className="mx-[15%]"
                    challenges={t("industry.industries.fintech.challenges", { returnObjects: true })}
                    solutions={t("industry.industries.fintech.solutions", { returnObjects: true })}
                    impact={t("industry.industries.fintech.impact", { returnObjects: true })}
                />
            </section>

            <section id="ecommerce" className="pb-10">
                <h2 className="subheading">{t("industry.industries.ecommerce.title")}</h2>
                <IndustryCard
                    className="mx-[15%]"
                    challenges={t("industry.industries.ecommerce.challenges", { returnObjects: true })}
                    solutions={t("industry.industries.ecommerce.solutions", { returnObjects: true })}
                    impact={t("industry.industries.ecommerce.impact", { returnObjects: true })}
                />
            </section>

            <section id="smb" className="pb-10">
                <h2 className="subheading">{t("industry.industries.smb.title")}</h2>
                <IndustryCard
                    className="mx-[15%]"
                    challenges={t("industry.industries.smb.challenges", { returnObjects: true })}
                    solutions={t("industry.industries.smb.solutions", { returnObjects: true })}
                    impact={t("industry.industries.smb.impact", { returnObjects: true })}
                />
            </section>

            <section id="agriculture" className="pb-10">
                <h2 className="subheading">{t("industry.industries.agriculture.title")}</h2>
                <IndustryCard
                    className="mx-[15%]"
                    challenges={t("industry.industries.agriculture.challenges", { returnObjects: true })}
                    solutions={t("industry.industries.agriculture.solutions", { returnObjects: true })}
                    impact={t("industry.industries.agriculture.impact", { returnObjects: true })}
                />
            </section>

            <section id="education" className="pb-10">
                <h2 className="subheading">{t("industry.industries.education.title")}</h2>
                <IndustryCard
                    className="mx-[15%]"
                    challenges={t("industry.industries.education.challenges", { returnObjects: true })}
                    solutions={t("industry.industries.education.solutions", { returnObjects: true })}
                    impact={t("industry.industries.education.impact", { returnObjects: true })}
                />
            </section>

            <section id="nonprofit" className="pb-10">
                <h2 className="subheading">{t("industry.industries.nonprofit.title")}</h2>
                <IndustryCard
                    className="mx-[15%]"
                    challenges={t("industry.industries.nonprofit.challenges", { returnObjects: true })}
                    solutions={t("industry.industries.nonprofit.solutions", { returnObjects: true })}
                    impact={t("industry.industries.nonprofit.impact", { returnObjects: true })}
                />
            </section>

            <section id="government" className="pb-10">
                <h2 className="subheading">{t("industry.industries.government.title")}</h2>
                <IndustryCard
                    className="mx-[15%]"
                    challenges={t("industry.industries.government.challenges", { returnObjects: true })}
                    solutions={t("industry.industries.government.solutions", { returnObjects: true })}
                    impact={t("industry.industries.government.impact", { returnObjects: true })}
                />
            </section>

            <section>
                <h2 className="subheading">{t("industry.otherIndustries.title")}</h2>

                <div className="rounded-2xl border p-6 border-gray-800 bg-gray-900 mx-[15%]">

                    <p className="text-xl font-medium text-white mb-4">
                        {t("industry.otherIndustries.subtitle")}
                    </p>

                    <div className="flex flex-wrap gap-2 mb-5">
                        {t("industry.otherIndustries.industries", { returnObjects: true }).map((industry) => (
                            <span
                                className="rounded-lg border px-3 py-1 text-lg border-gray-700 bg-gray-800 text-gray-300"
                            >
                                {industry}
                            </span>
                        ))}
                    </div>

                    <div className="border-t border-gray-700 pt-4">
                        <p className="xl font-medium uppercase tracking-widest text-gray-600 mb-3">
                            {t("industry.otherIndustries.foundationTitle")}
                        </p>

                        <div className="flex flex-wrap gap-2">
                            {t("industry.otherIndustries.features", { returnObjects: true }).map((feature) => (
                                <span
                                    className="inline-flex items-center gap-1.5 rounded-lg border px-3 py-1 text-lg bg-blue-950 border-blue-900 text-blue-300"
                                >
                                    <CheckCircle2 className="h-3 w-3 stroke-blue-400" strokeWidth={2} />
                                    {feature}
                                </span>
                            ))}
                        </div>
                    </div>

                </div>
            </section>

            <section className="px-8 py-16 max-w-4xl mx-auto">
                <h2 className="subheading">{t("industry.advantage.title")}</h2>
                <p className="subtext">{t("industry.advantage.subtitle")}</p>

                <SymmetricalChecklist
                    items={t("industry.advantage.items", { returnObjects: true })}
                    size={3.5}
                />
            </section>

        </div>
    );
}