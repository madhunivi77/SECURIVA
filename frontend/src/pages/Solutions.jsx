import {
  Cpu, ShieldCheck, Globe, Users, BookOpen,
  Puzzle, Sparkles, LayoutDashboard, Bot,
  Settings, DollarSign, Lightbulb, Layers, Heart
} from "lucide-react";
import ReasonCard from "../components/ReasonCard";
import SolutionCard from "../components/SolutionCard";

const solutions = [
  {
    number: "01",
    icon: Cpu,
    label: "AI Business Automation",
    description: "Automate workflows, scheduling, communication, and reporting across your organization.",
    points: [
      "Smart task management and workflow optimization",
      "Calendar and email synchronization (Gmail, Outlook, etc.)",
      "Integration with CRMs, project tools, and fintech platforms",
      "Auto-generated reports and business summaries",
    ],
    imageLink: "solutions/AI Business Automation.png",
    altText: "AI Business Automation Icon"
  },
  {
    number: "02",
    icon: ShieldCheck,
    label: "Cybersecurity & Data Protection",
    description: "Keep your business safe with real-time AI monitoring and adaptive security protocols.",
    points: [
      "AI-driven threat detection and prevention",
      "Endpoint and cloud protection",
      "Identity and access management with biometric analysis",
      "Real-time alerts for suspicious behavior or phishing activity",
    ],
    imageLink: "solutions/Cybersecurity & Data Protection.png",
    altText: "Cybersecurity & Data Protection Icon"
  },
  {
    number: "03",
    icon: Globe,
    label: "AI-Managed VPN",
    description: "Protect every interaction with a built-in VPN powered by AI.",
    points: [
      "Encrypted communications for calls, emails, and data transfers",
      "Dynamic routing for the fastest and safest connections",
      "Built-in threat analysis within the VPN layer",
      "Compliance with GDPR, HIPAA, and PCI-DSS",
    ],
    imageLink: "solutions/AI-Managed VPN (Secure Connectivity).png",
    altText: "AI-Managed VPN Icon"
  },
  {
    number: "04",
    icon: Users,
    label: "Customer Interaction & Communication",
    description: "Engage with clients through human-like conversations, voice calls, and emails.",
    points: [
      "Multichannel assistant: calls, emails, chats, social media, and video",
      "AI avatar for customer support and onboarding",
      "Personalized follow-ups and smart responses",
      "CRM integration for seamless client tracking",
    ],
    imageLink: "solutions/Customer Interaction & Communication.png",
    altText: "Customer Interaction & Communication"
  },
  {
    number: "05",
    icon: BookOpen,
    label: "eBook & Training Content Generation",
    description: "Transform technical knowledge into easy-to-understand eBooks, manuals, or awareness guides.",
    points: [
      "Auto-generate professional eBooks and cybersecurity training materials",
      "Templates for guides, safety checklists, and onboarding manuals",
      "Export options: PDF, EPUB, and web format",
    ],
    examples: [
      "Cybersecurity for Beginners: Staying Safe Online",
      "Data Protection Handbook for Small Businesses",
    ],
    imageLink: "solutions/eBook & Training Content Generation.png",
    altText: "eBook & Training Content Generation Icon"
  },
  {
    number: "06",
    icon: Puzzle,
    label: "Cross-Platform Integrations",
    description: "Connect SecuriVA with your favorite platforms and tools.",
    points: [
      "WhatsApp, Gmail, Microsoft 365, Slack, Salesforce, OpenAI",
      "Financial systems and fintech APIs",
      "HTTP request builder for custom integrations",
    ],
    imageLink: "solutions/Cross-Platform Integrations.png",
    altText: "Cross-Platform Integrations Icon"
  },
  {
    number: "07",
    icon: Sparkles,
    label: "AI-Powered Business Digital Twin",
    description: "Experience the next evolution in business intelligence.",
    points: [
      "Create a digital replica of your business operations",
      "Simulate workflows, predict risks, and suggest optimizations",
      "Identify cyber vulnerabilities before they happen",
      "Enable predictive decision-making and automated corrections",
    ],
    isFuture: true,
    imageLink: "solutions/AI-Powered Business Digital Twin.png",
    altText: "AI Powered Business Digital Twin Icon"
  },
];

const reasons = [
  {
    icon: LayoutDashboard,
    label: "All-in-One Intelligence Platform",
    description: "One unified hub combining AI automation, cybersecurity, VPN, and customer engagement. No need for multiple tools — SecuriVA centralizes everything.",
  },
  {
    icon: ShieldCheck,
    label: "Enterprise-Grade Security",
    description: "Built with cyber defense and privacy by design, ensuring all data, messages, and calls are encrypted and monitored safely by AI.",
  },
  {
    icon: Bot,
    label: "Real AI Assistant with a Human Touch",
    description: "SecuriVA's AI Avatar can speak, chat, and interact naturally with users, providing a human-like experience with the efficiency of automation.",
  },
  {
    icon: Globe,
    label: "Seamless Ecosystem Integration",
    description: "Integrates smoothly with cloud services, CRMs, email platforms, and fintech systems, adapting to any business niche.",
  },
  {
    icon: Settings,
    label: "Customizable for Any Industry",
    description: "From finance to education to e-commerce — SecuriVA adapts to unique workflows, compliance needs, and automation goals.",
  },
  {
    icon: DollarSign,
    label: "Scalable Monetization Options",
    description: "Choose from SaaS subscriptions, usage-based billing, or white-label licensing for enterprise clients.",
  },
  {
    icon: Lightbulb,
    label: "Backed by Innovation",
    description: "Powered by Kimuntu Power Inc. and built on AWS cloud infrastructure, SecuriVA integrates OpenAI, TensorFlow, and adaptive AI security modules.",
  },
  {
    icon: Layers,
    label: "Future-Ready Platform",
    description: "Designed for continuous evolution — upcoming features like the Digital Twin, AI VPN enhancements, and threat intelligence dashboards keep businesses ahead.",
  },
  {
    icon: Heart,
    label: "Built for People, Trusted by Professionals",
    description: "Our mission: simplify technology, amplify security, and empower businesses of all sizes to operate smarter and safer.",
  },
];


export default function Solutions() {

  return (
    <div className="bg-gray-900 text-white">

      {/* ---------- HERO ---------- */}
      <section className="hero py-24 bg-linear-to-br from-blue-900 to-black text-white">
        <div className="hero-content text-center max-w-4xl">
          <div>
            <h1 className="text-5xl font-bold mb-6">Solutions</h1>
            <p className="text-xl opacity-90">
              SecuriVA merges AI intelligence, cybersecurity, and virtual collaboration into one secure
              ecosystem — designed to automate, protect, and optimize modern businesses.
            </p>
          </div>
        </div>
      </section>

      {/* Solution Cards */}
      <section className="flex flex-col gap-6 mx-[15%] my-10">
        {solutions.map((solution) => (
          <SolutionCard key={solution.number} {...solution} />
        ))}
      </section>

      <section className="px-8 py-16 max-w-6xl mx-auto">

        {/* Header */}
        <div className="text-center mb-10">
          <h2 className="text-4xl font-normal text-gray-900 mb-3 dark:text-white">
            Why Choose SecuriVA
          </h2>
          <p className="text-[15px] font-light text-gray-500 max-w-xl mx-auto leading-relaxed dark:text-gray-400">
            SecuriVA isn't just another virtual assistant — it's your AI-powered business partner for automation, security, and growth.
          </p>
        </div>

        {/* Reason Cards */}
        <div className="flex flex-wrap justify-center gap-3 mb-10">
          {reasons.map((reason) => (
            <ReasonCard key={reason.label} {...reason} />
          ))}
        </div>

        {/* Closing Quote */}
        <div className="rounded-2xl border border-blue-100 bg-blue-50 px-8 py-6 text-center dark:border-blue-900 dark:bg-blue-950">
          <p className="text-[15px] font-light italic text-blue-700 dark:text-blue-300">
            "With SecuriVA, your business doesn't just work — it learns, protects, and grows."
          </p>
        </div>

      </section>
    </div>
  );
}