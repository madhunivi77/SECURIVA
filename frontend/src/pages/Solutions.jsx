import {
  Cpu, ShieldCheck, Globe, Users, BookOpen,
  Puzzle, Sparkles, LayoutDashboard, Bot,
  Settings, DollarSign, Lightbulb, Layers, Heart,
  ChevronRight
} from "lucide-react";

import ReasonCard from "../components/ReasonCard";
import SolutionCard from "../components/SolutionCard";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

const solutionsConfig = (t) => [
  {
    number: "01",
    icon: Cpu,
    label: t("solutions.solutionsList.aiAutomation.label"),
    description: t("solutions.solutionsList.aiAutomation.description"),
    points: t("solutions.solutionsList.aiAutomation.points", { returnObjects: true }),
    imageLink: "solutions/AI Business Automation.png",
    altText: t("solutions.solutionsList.aiAutomation.imageAlt")
  },
  {
    number: "02",
    icon: ShieldCheck,
    label: t("solutions.solutionsList.cybersecurity.label"),
    description: t("solutions.solutionsList.cybersecurity.description"),
    points: t("solutions.solutionsList.cybersecurity.points", { returnObjects: true }),
    imageLink: "solutions/Cybersecurity & Data Protection.png",
    altText: t("solutions.solutionsList.cybersecurity.imageAlt")
  },
  {
    number: "03",
    icon: Globe,
    label: t("solutions.solutionsList.vpn.label"),
    description: t("solutions.solutionsList.vpn.description"),
    points: t("solutions.solutionsList.vpn.points", { returnObjects: true }),
    imageLink: "solutions/AI-Managed VPN (Secure Connectivity).png",
    altText: t("solutions.solutionsList.vpn.imageAlt")
  },
  {
    number: "04",
    icon: Users,
    label: t("solutions.solutionsList.communication.label"),
    description: t("solutions.solutionsList.communication.description"),
    points: t("solutions.solutionsList.communication.points", { returnObjects: true }),
    imageLink: "solutions/Customer Interaction & Communication.png",
    altText: t("solutions.solutionsList.communication.imageAlt")
  },
  {
    number: "05",
    icon: BookOpen,
    label: t("solutions.solutionsList.ebook.label"),
    description: t("solutions.solutionsList.ebook.description"),
    points: t("solutions.solutionsList.ebook.points", { returnObjects: true }),
    examples: t("solutions.solutionsList.ebook.examples", { returnObjects: true }),
    imageLink: "solutions/eBook & Training Content Generation.png",
    altText: t("solutions.solutionsList.ebook.imageAlt")
  },
  {
    number: "06",
    icon: Puzzle,
    label: t("solutions.solutionsList.integrations.label"),
    description: t("solutions.solutionsList.integrations.description"),
    points: t("solutions.solutionsList.integrations.points", { returnObjects: true }),
    imageLink: "solutions/Cross-Platform Integrations.png",
    altText: t("solutions.solutionsList.integrations.imageAlt")
  },
  {
    number: "07",
    icon: Sparkles,
    label: t("solutions.solutionsList.digitalTwin.label"),
    description: t("solutions.solutionsList.digitalTwin.description"),
    points: t("solutions.solutionsList.digitalTwin.points", { returnObjects: true }),
    isFuture: true,
    imageLink: "solutions/AI-Powered Business Digital Twin.png",
    altText: t("solutions.solutionsList.digitalTwin.imageAlt")
  },
];

const reasonsConfig = (t) => [
  {
    icon: LayoutDashboard,
    label: t("solutions.reasons.items.platform.label"),
    description: t("solutions.reasons.items.platform.description"),
  },
  {
    icon: ShieldCheck,
    label: t("solutions.reasons.items.security.label"),
    description: t("solutions.reasons.items.security.description"),
  },
  {
    icon: Bot,
    label: t("solutions.reasons.items.aiAssistant.label"),
    description: t("solutions.reasons.items.aiAssistant.description"),
  },
  {
    icon: Globe,
    label: t("solutions.reasons.items.ecosystem.label"),
    description: t("solutions.reasons.items.ecosystem.description"),
  },
  {
    icon: Settings,
    label: t("solutions.reasons.items.customizable.label"),
    description: t("solutions.reasons.items.customizable.description"),
  },
  {
    icon: DollarSign,
    label: t("solutions.reasons.items.monetization.label"),
    description: t("solutions.reasons.items.monetization.description"),
  },
  {
    icon: Lightbulb,
    label: t("solutions.reasons.items.innovation.label"),
    description: t("solutions.reasons.items.innovation.description"),
  },
  {
    icon: Layers,
    label: t("solutions.reasons.items.future.label"),
    description: t("solutions.reasons.items.future.description"),
  },
  {
    icon: Heart,
    label: t("solutions.reasons.items.people.label"),
    description: t("solutions.reasons.items.people.description"),
  },
];

export default function Solutions() {
  const { t } = useTranslation();

  const solutions = solutionsConfig(t);
  const reasons = reasonsConfig(t);

  return (
    <div className="bg-gray-900 text-white">

      {/* HERO */}
      <section className="hero py-24 bg-linear-to-br from-blue-900 to-black text-white">
        <div className="hero-content text-center max-w-4xl">
          <div>
            <h1 className="text-5xl font-bold mb-6">
              {t("solutions.hero.title")}
            </h1>
            <p className="text-xl opacity-90">
              {t("solutions.hero.subtitle")}
            </p>
          </div>
        </div>
      </section>

      {/* SOLUTIONS */}
      <section className="flex flex-col gap-6 mx-[15%] my-10">
        {solutions.map((solution) => (
          <SolutionCard key={solution.number} {...solution} />
        ))}
      </section>

      {/* WHY SECTION */}
      <section className="px-8 py-16 max-w-6xl mx-auto">

        <div className="text-center mb-10">
          <h2 className="text-4xl font-normal text-gray-900 mb-3 dark:text-white">
            {t("solutions.reasonsTitle")}
          </h2>
          <p className="text-[15px] font-light text-gray-500 max-w-xl mx-auto leading-relaxed dark:text-gray-400">
            {t("solutions.reasonsSubtitle")}
          </p>
        </div>

        <div className="flex flex-wrap justify-center gap-3 mb-10">
          {reasons.map((reason) => (
            <ReasonCard key={reason.label} {...reason} />
          ))}
        </div>

        <div className="rounded-2xl border border-blue-100 bg-blue-50 px-8 py-6 text-center dark:border-blue-900 dark:bg-blue-950">
          <p className="text-[15px] font-light italic text-blue-700 dark:text-blue-300">
            {t("solutions.quote")}
          </p>
        </div>

        <div className="flex justify-center">
          <Link to={"/industries"}>
            <button className="flex justify-center items-center btn bg-blue-900 mt-10">
              {t("solutions.button")}
              <ChevronRight />
            </button>
          </Link>
        </div>

      </section>
    </div>
  );
}