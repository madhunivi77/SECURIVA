import { Link } from "react-router-dom";
import Sponsors from "../components/Sponsors";
import {
  Phone,
  Calendar,
  MessageCircle,
  Zap,
  Activity,
  Lock,
  ShieldCheck,
  Server,
  Mail,
  MessageSquare,
  FileText,
  Workflow,
  MousePointerClick,
  ShieldAlert,
  Network,
  KeyRound,
  Layers,
  Globe,
  Settings,
  SlidersHorizontal,
  BadgeCheck,
  Play,
  BookOpen,
  ChevronRight
} from "lucide-react";

import CapabilityCard from "../components/CapabilityCard";
import SymmetricalChecklist from "../components/SymmetricalChecklist";
import { useTranslation } from "react-i18next";

export default function Features() {
  const { t } = useTranslation();

  const CapabilityCards = ({ cards }) => (
    <div className="flex flex-wrap gap-3 mb-6 mx-[15%]">
      {cards.map((card) => (
        <CapabilityCard
          className="sm:min-w-[35%] min-w-[70%]"
          key={card.label}
          {...card}
        />
      ))}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">

      {/* ---------- HERO ---------- */}
      <section className="hero py-24 bg-linear-to-br from-blue-900 to-black text-white">
        <div className="hero-content text-center max-w-4xl">
          <div>
            <h1 className="text-5xl font-bold mb-6">
              {t("features.hero.title")}
            </h1>

            <p className="text-xl opacity-90">
              {t("features.hero.description")}
            </p>
          </div>
        </div>
      </section>

      {/* ---------- AI AGENT ---------- */}
      <section className="relative overflow-hidden px-8 py-12">

        <h2 className="text-4xl font-normal text-center text-gray-900 mb-2 dark:text-white">
          {t("features.sections.aiAgent.title")}
        </h2>

        <p className="text-xl font-light text-gray-500 mb-8 text-center dark:text-gray-400 mx-[15%]">
          {t("features.sections.aiAgent.subtitle")}
        </p>

        <div className="border-t border-gray-100 mb-8 dark:border-gray-800" />

        <div className="mx-[15%] pb-5 text-xl">
          {t("features.sections.aiAgent.description")}
        </div>

        <CapabilityCards
          cards={[
            {
              icon: Phone,
              label: t("features.sections.aiAgent.cards.callManagement.label"),
              description: t("features.sections.aiAgent.cards.callManagement.description"),
            },
            {
              icon: Calendar,
              label: t("features.sections.aiAgent.cards.scheduling.label"),
              description: t("features.sections.aiAgent.cards.scheduling.description"),
            },
            {
              icon: MessageCircle,
              label: t("features.sections.aiAgent.cards.multichannel.label"),
              description: t("features.sections.aiAgent.cards.multichannel.description"),
            },
            {
              icon: Zap,
              label: t("features.sections.aiAgent.cards.integrations.label"),
              description: t("features.sections.aiAgent.cards.integrations.description"),
            },
          ]}
        />

        <SymmetricalChecklist
          className="mx-[15%]"
          heading={t("features.sections.aiAgent.advantages.title")}
          items={t("features.sections.aiAgent.advantages.items", { returnObjects: true })}
        />

        <div className="flex justify-center">
          <Link to="/agent-voice">
            <button className="flex justify-center items-center btn bg-blue-900 mt-10">
              {t("features.sections.aiAgent.cta.button")}
              <ChevronRight />
            </button>
          </Link>
        </div>
      </section>

      {/* ---------- CYBERSECURITY ---------- */}
      <section className="relative overflow-hidden px-8 py-12">

        <h2 className="text-4xl font-normal text-center text-gray-900 mb-2 dark:text-white">
          {t("features.sections.cybersecurity.title")}
        </h2>

        <p className="text-xl font-light text-gray-500 mb-8 text-center dark:text-gray-400 mx-[15%]">
          {t("features.sections.cybersecurity.subtitle")}
        </p>

        <div className="border-t border-gray-100 mb-8 dark:border-gray-800" />

        <div className="mx-[15%] pb-5 text-xl">
          {t("features.sections.cybersecurity.description")}
        </div>

        <CapabilityCards
          cards={[
            {
              icon: Activity,
              label: t("features.sections.cybersecurity.cards.monitoring.label"),
              description: t("features.sections.cybersecurity.cards.monitoring.description"),
            },
            {
              icon: Lock,
              label: t("features.sections.cybersecurity.cards.encryption.label"),
              description: t("features.sections.cybersecurity.cards.encryption.description"),
            },
            {
              icon: ShieldCheck,
              label: t("features.sections.cybersecurity.cards.compliance.label"),
              description: t("features.sections.cybersecurity.cards.compliance.description"),
            },
            {
              icon: Server,
              label: t("features.sections.cybersecurity.cards.vulnerability.label"),
              description: t("features.sections.cybersecurity.cards.vulnerability.description"),
            },
          ]}
        />

        <SymmetricalChecklist
          className="mx-[15%]"
          heading={t("features.sections.cybersecurity.advantages.title")}
          items={t("features.sections.cybersecurity.advantages.items", { returnObjects: true })}
        />
      </section>

      {/* ---------- TEXT AGENT ---------- */}
      <section className="relative overflow-hidden px-8 py-12">

        <h2 className="text-4xl font-normal text-center text-gray-900 mb-2 dark:text-white">
          {t("features.sections.textAgent.title")}
        </h2>

        <p className="text-xl font-light text-gray-500 mb-8 text-center dark:text-gray-400 mx-[15%]">
          {t("features.sections.textAgent.subtitle")}
        </p>

        <div className="border-t border-gray-100 mb-8 dark:border-gray-800" />

        <div className="mx-[15%] pb-5 text-xl">
          {t("features.sections.textAgent.description")}
        </div>

        <CapabilityCards
          cards={[
            {
              icon: Mail,
              label: t("features.sections.textAgent.cards.email.label"),
              description: t("features.sections.textAgent.cards.email.description"),
            },
            {
              icon: MessageSquare,
              label: t("features.sections.textAgent.cards.chat.label"),
              description: t("features.sections.textAgent.cards.chat.description"),
            },
            {
              icon: FileText,
              label: t("features.sections.textAgent.cards.documents.label"),
              description: t("features.sections.textAgent.cards.documents.description"),
            },
            {
              icon: Workflow,
              label: t("features.sections.textAgent.cards.automation.label"),
              description: t("features.sections.textAgent.cards.automation.description"),
            },
          ]}
        />

        <SymmetricalChecklist
          className="mx-[15%]"
          heading={t("features.sections.textAgent.advantages.title")}
          items={t("features.sections.textAgent.advantages.items", { returnObjects: true })}
        />
      </section>

      {/* ---------- VPN ---------- */}
      <section className="relative overflow-hidden px-8 py-12">

        <h2 className="text-4xl font-normal text-center text-gray-900 mb-2 dark:text-white">
          {t("features.sections.vpn.title")}
        </h2>

        <p className="text-xl font-light text-gray-500 mb-8 text-center dark:text-gray-400 mx-[15%]">
          {t("features.sections.vpn.subtitle")}
        </p>

        <div className="border-t border-gray-100 mb-8 dark:border-gray-800" />

        <div className="mx-[15%] pb-5 text-xl">
          {t("features.sections.vpn.description")}
        </div>

        <CapabilityCards
          cards={[
            {
              icon: MousePointerClick,
              label: t("features.sections.vpn.cards.secureBrowsing.label"),
              description: t("features.sections.vpn.cards.secureBrowsing.description"),
            },
            {
              icon: ShieldAlert,
              label: t("features.sections.vpn.cards.aiThreat.label"),
              description: t("features.sections.vpn.cards.aiThreat.description"),
            },
            {
              icon: Network,
              label: t("features.sections.vpn.cards.routing.label"),
              description: t("features.sections.vpn.cards.routing.description"),
            },
            {
              icon: KeyRound,
              label: t("features.sections.vpn.cards.mfa.label"),
              description: t("features.sections.vpn.cards.mfa.description"),
            },
          ]}
        />

        <SymmetricalChecklist
          className="mx-[15%]"
          heading={t("features.sections.vpn.advantages.title")}
          items={t("features.sections.vpn.advantages.items", { returnObjects: true })}
        />
      </section>

      {/* ---------- RECAP ---------- */}
      <section className="relative overflow-hidden px-8 py-12 mx-[15%]">

        <h2 className="text-4xl font-normal text-center text-gray-900 mb-2 dark:text-white">
          {t("features.sections.recap.title")}
        </h2>

        <div className="flex flex-wrap justify-center gap-3 mb-6">
          {[
            "allInOne",
            "crossIndustry",
            "automationSecurity",
            "customizable",
            "compliance"
          ].map((key) => (
            <CapabilityCard
              key={key}
              icon={{
                allInOne: Layers,
                crossIndustry: Globe,
                automationSecurity: Settings,
                customizable: SlidersHorizontal,
                compliance: BadgeCheck
              }[key]}
              label={t(`features.sections.recap.cards.${key}.label`)}
              description={t(`features.sections.recap.cards.${key}.description`)}
              className="sm:min-w-[35%] min-w-[70%] max-w-[50%]"
            />
          ))}
        </div>
      </section>

      {/* ---------- CTA ---------- */}
      <section className="px-8 py-16 text-center">

        <h2 className="text-4xl font-normal text-gray-900 mb-3 dark:text-white">
          {t("features.sections.cta.title")}
        </h2>

        <p className="text-[15px] font-light text-gray-500 mb-10 max-w-lg mx-auto dark:text-gray-400">
          {t("features.sections.cta.description")}
        </p>

        <div className="flex flex-wrap justify-center gap-3">

          <Link to="/contact">
            <button className="flex items-center gap-2 rounded-xl bg-red-500 px-6 py-3 text-[14px] font-medium text-white">
              <Play className="h-4 w-4 fill-white stroke-none" />
              {t("features.sections.cta.buttons.demo")}
            </button>
          </Link>

          <button
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
            className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-6 py-3 text-[14px] font-medium text-gray-800"
          >
            <BookOpen className="h-4 w-4" />
            {t("features.sections.cta.buttons.learn")}
          </button>

          <Link to="/contact">
            <button className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-6 py-3 text-[14px] font-medium text-gray-800">
              <Mail className="h-4 w-4" />
              {t("features.sections.cta.buttons.contact")}
            </button>
          </Link>

        </div>
      </section>

      <Sponsors className="bg-white mt-10 pt-5 text-center text-black text-3xl" />
    </div>
  );
}