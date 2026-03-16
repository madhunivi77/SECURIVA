import {
  Cpu, ShieldCheck, Globe, Users, BookOpen,
  Puzzle, Sparkles, CheckCircle2, Zap, LayoutDashboard, Bot,
  Settings, DollarSign, Lightbulb, Layers, Heart
} from "lucide-react";
import { useTheme } from "../context/ThemeContext";

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


const SolutionCard = ({ number, icon: Icon, label, description, points, examples, isFuture }) => (
  <div className="flex gap-6 rounded-2xl border border-gray-100 bg-white p-6 hover:border-gray-200 transition-colors dark:border-gray-800 dark:bg-inherit dark:hover:border-gray-700">

    {/* Left: number + icon */}
    <div className="flex flex-col items-center gap-3 pt-1">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-950">
        <Icon className="h-5 w-5 stroke-blue-600 dark:stroke-blue-400" strokeWidth={1.5} />
      </div>
      <span className="text-lg font-medium tabular-nums text-gray-300 dark:text-gray-700">{number}</span>
    </div>

    {/* Right: content */}
    <div className="flex-1 min-w-0">
      <div className="flex flex-wrap items-center gap-2 mb-1">
        <h3 className="text-xl font-medium text-gray-900 dark:text-white">{label}</h3>
        {isFuture && (
          <span className="inline-flex items-center gap-1 rounded-full border border-purple-200 bg-purple-50 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-purple-600 dark:border-purple-800 dark:bg-purple-950 dark:text-purple-400">
            <Zap className="h-2.5 w-2.5 fill-purple-500 stroke-none" />
            Coming Soon
          </span>
        )}
      </div>
      <p className="text-lg text-gray-500 mb-3 leading-relaxed dark:text-gray-400">{description}</p>
      <ul className="flex flex-col gap-1.5">
        {points.map((point) => (
          <li key={point} className="flex items-start gap-2 text-lg text-gray-700 dark:text-gray-300">
            <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 stroke-blue-500 dark:stroke-blue-400" strokeWidth={2} />
            {point}
          </li>
        ))}
      </ul>
      {examples && (
        <div className="mt-3 flex flex-wrap gap-2">
          {examples.map((ex) => (
            <span key={ex} className="rounded-lg border border-gray-100 bg-gray-50 px-3 py-1 text-[12px] italic text-gray-500 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-400">
              "{ex}"
            </span>
          ))}
        </div>
      )}
    </div>

  </div>
);


const ReasonCard = ({ icon: Icon, label, description }) => {
    const {theme} = useTheme();
    return (
        <div className={`flex flex-col gap-3 rounded-2xl border border-gray-100 p-5 hover:border-gray-200 transition-colors dark:border-gray-800 bg-[${theme.bg}] dark:hover:border-gray-700 flex-1 min-w-65 max-w-1/3`}>
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-950">
            <Icon className="h-4 w-4 stroke-blue-600 dark:stroke-blue-400" strokeWidth={1.5} />
            </div>
            <div>
            <p className="text-lg font-medium text-gray-900 mb-1 dark:text-white">{label}</p>
            <p className="text-md text-gray-500 leading-relaxed dark:text-gray-400">{description}</p>
            </div>
        </div>
    );
};

export default function Solutions(){

    return(
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

    <section className="px-8 py-16 max-w-4xl mx-auto">

        {/* Header */}
        <div className="text-center mb-10">
        <h2 className="text-4xl font-normal text-gray-900 mb-3 dark:text-white">
            Why Choose <span className="italic text-blue-600 dark:text-blue-400">SecuriVA</span>
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