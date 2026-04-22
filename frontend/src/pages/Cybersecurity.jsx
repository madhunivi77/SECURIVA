import {
  BadgeCheck,
  CircleDollarSign,
  GlobeLock,
  Lock,
  Phone,
  Play,
  SearchCode,
  ShieldAlert,
  Target,
  Handshake,
  Files,
  Cctv,
  BrickWallShield,
  Expand,
  ChartNoAxesCombined,
} from "lucide-react";

import { Link } from "react-router-dom";
import CapabilityCard from "../components/CapabilityCard";
import SolutionCard from "../components/SolutionCard";
import ReasonCard from "../components/ReasonCard";
import SymmetricalChecklist from "../components/SymmetricalChecklist";
import Checklist from "../components/Checklist";
import { useTranslation } from "react-i18next";

export default function Cybersecurity() {
  const { t } = useTranslation();

  const reasons = [
    {
      icon: BrickWallShield,
      label: t("cybersecurity.reasons.integrated.label"),
      description: t("cybersecurity.reasons.integrated.description"),
    },
    {
      icon: Cctv,
      label: t("cybersecurity.reasons.threatIntelligence.label"),
      description: t("cybersecurity.reasons.threatIntelligence.description"),
    },
    {
      icon: BadgeCheck,
      label: t("cybersecurity.reasons.compliance.label"),
      description: t("cybersecurity.reasons.compliance.description"),
    },
    {
      icon: Expand,
      label: t("cybersecurity.reasons.scalable.label"),
      description: t("cybersecurity.reasons.scalable.description"),
    },
    {
      icon: ChartNoAxesCombined,
      label: t("cybersecurity.reasons.continuous.label"),
      description: t("cybersecurity.reasons.continuous.description"),
    },
  ];

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">

      {/* ---------- HERO ---------- */}
      <section className="hero py-24 bg-linear-to-br bg-[#0a0f1f] text-white">
        <div className="hero-content text-center max-w-4xl">
          <div>
            <h1 className="text-5xl font-bold mb-6">
              {t("cybersecurity.hero.title")}
            </h1>
            <p className="text-xl opacity-90">
              {t("cybersecurity.hero.description")}
            </p>
          </div>
        </div>
      </section>

      {/* ---------- VIDEO ---------- */}
      <section className="relative overflow-hidden">
        <div className="relative w-full h-[400px] overflow-hidden bg-black mx-auto">
          <video
            autoPlay
            loop
            muted
            playsInline
            className="absolute top-0 left-0 w-full object-cover opacity-40"
          >
            <source src="Cybersecurity_video.mp4" type="video/mp4" />
          </video>

          <div className="absolute top-0 left-0 w-full h-64 bg-gradient-to-b from-[#0a0f1f] via-[#0a0f1f]/60 to-transparent pointer-events-none" />
          <div className="absolute bottom-0 left-0 w-full h-64 bg-gradient-to-t from-[#131827] via-gray-black/60 to-transparent pointer-events-none" />

          <div className="relative max-w-6xl mx-auto -mt-10">
            <h2 className="subheading">
              {t("cybersecurity.video.title")}
            </h2>

            <p className="text-center card p-12 mx-[15%] backdrop-blur bg-gray-800/50 shadow-lg text-xl">
              {t("cybersecurity.video.description")}
            </p>
          </div>
        </div>
      </section>

      {/* ---------- FUNDAMENTALS ---------- */}
      <section className="flex flex-col gap-5 mb-5 -mt-20 mx-[15%]">
        <h2 className="subheading pt-10 mb-12 text-center">
          {t("cybersecurity.fundamentals.title")}
        </h2>

        <CapabilityCard
          icon={GlobeLock}
          label={t("cybersecurity.fundamentals.encryption.label")}
          description={t("cybersecurity.fundamentals.encryption.description")}
        />

        <CapabilityCard
          icon={ShieldAlert}
          label={t("cybersecurity.fundamentals.threat.label")}
          description={t("cybersecurity.fundamentals.threat.description")}
        />

        <CapabilityCard
          icon={SearchCode}
          label={t("cybersecurity.fundamentals.vulnerability.label")}
          description={t("cybersecurity.fundamentals.vulnerability.description")}
        />

        <CapabilityCard
          icon={BadgeCheck}
          label={t("cybersecurity.fundamentals.compliance.label")}
          description={t("cybersecurity.fundamentals.compliance.description")}
        />
      </section>

      {/* ---------- VALUE ---------- */}
      <h2 className="subheading">
        {t("cybersecurity.value.title")}
      </h2>

      <p className="subtext">
        {t("cybersecurity.value.description")}
      </p>

      <section className="gap-5 my-5 mx-[15%]">
        <SymmetricalChecklist
          heading={t("cybersecurity.protection.heading")}
          items={t("cybersecurity.protection.items", { returnObjects: true })}
        />
      </section>

      {/* ---------- CORE ---------- */}
      <section className="flex flex-col gap-5 my-5 mx-[15%]">

        <SolutionCard
          number="01"
          icon={Target}
          label={t("cybersecurity.core.title")}
          content={
            <div>
              <h3 className="text-lg text-gray-500 my-3 dark:text-gray-400">
                {t("cybersecurity.core.framework.title")}
              </h3>

              <Checklist
                items={t("cybersecurity.core.framework.items1", { returnObjects: true })}
                size="3.5"
              />

              <h3 className="text-lg text-gray-500 my-3 dark:text-gray-400">
                {t("cybersecurity.core.monitoring.title")}
              </h3>

              <Checklist
                items={t("cybersecurity.core.monitoring.items", { returnObjects: true })}
                size="3.5"
              />
            </div>
          }
        />

        <SolutionCard
          number="02"
          icon={CircleDollarSign}
          label={t("cybersecurity.cost.title")}
          description={t("cybersecurity.cost.description")}
          points={t("cybersecurity.cost.items", { returnObjects: true })}
          footer={t("cybersecurity.cost.footer")}
        />

        <SolutionCard
          number="03"
          icon={Handshake}
          label={t("cybersecurity.partnership.title")}
          description={t("cybersecurity.partnership.description")}
          points={t("cybersecurity.partnership.items", { returnObjects: true })}
          footer={t("cybersecurity.partnership.footer")}
        />

        <SolutionCard
          number="04"
          icon={Files}
          label={t("cybersecurity.resources.title")}
          description={t("cybersecurity.resources.description")}
          points={t("cybersecurity.resources.items", { returnObjects: true })}
          footer={t("cybersecurity.resources.footer")}
        />
      </section>

      {/* ---------- REASONS ---------- */}
      <h2 className="subheading">
        {t("cybersecurity.reasons.title")}
      </h2>

      <section className="gap-5 my-5 mx-[15%]">
        <div className="flex flex-wrap justify-center gap-3 mb-10">
          {reasons.map((reason) => (
            <ReasonCard
              key={reason.label}
              icon={reason.icon}
              label={reason.label}
              description={reason.description}
            />
          ))}
        </div>
      </section>

      {/* ---------- CTA ---------- */}
      <section className="px-8 py-16 text-center">
        <h2 className="text-4xl font-normal text-gray-900 mb-3 dark:text-white">
          {t("cybersecurity.cta.title")}
        </h2>

        <p className="text-2xl font-light text-gray-500 mb-10 max-w-xl mx-auto dark:text-gray-400">
          {t("cybersecurity.cta.description")}
        </p>

        <div className="flex flex-wrap justify-center gap-3">

          <Link to="/contact">
            <button className="flex items-center gap-2 rounded-xl bg-red-500 px-6 py-3 text-[14px] font-medium text-white">
              <Play className="h-4 w-4 fill-white stroke-none" />
              {t("cybersecurity.cta.demo")}
            </button>
          </Link>

          <Link to="/cybersecurity">
            <button
              onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
              className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-6 py-3 text-[14px] font-medium"
            >
              <Lock className="h-4 w-4 stroke-gray-500" />
              {t("cybersecurity.cta.docs")}
            </button>
          </Link>

          <Link to="/contact">
            <button className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-6 py-3 text-[14px] font-medium">
              <Phone className="h-4 w-4 stroke-gray-500" />
              {t("cybersecurity.cta.contact")}
            </button>
          </Link>

        </div>
      </section>

    </div>
  );
}