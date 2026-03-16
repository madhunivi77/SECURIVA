// About.jsx
import Sponsors from "../components/Sponsors";
import { useTheme } from "../context/ThemeContext";
import { Check, Phone, Calendar, MessageCircle, Zap, Activity, Lock, ShieldCheck, Server, Mail, MessageSquare, FileText, Workflow, MousePointerClick, ShieldAlert, Network, KeyRound } from "lucide-react";

export default function Features() {
  const { theme } = useTheme();

  const CapabilityCard = ({ icon: Icon, label, description }) => (
    <div className="flex items-start gap-3.5 rounded-xl border border-gray-100 bg-gray-50 p-4 transition-colors hover:border-gray-200 dark:border-gray-800 dark:bg-gray-900 dark:hover:border-gray-700 flex-1 sm:min-w-[35%] min-w-[70%]">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-50 dark:bg-blue-950">
        <Icon className="h-4 w-4 stroke-blue-600 dark:stroke-blue-400" strokeWidth={1.5} />
      </div>
      <div>
        <p className="text-[15px] font-medium text-gray-900 mb-0.5 dark:text-white">{label}</p>
        <p className="text-sm text-gray-500 leading-relaxed dark:text-gray-400">{description}</p>
      </div>
    </div>
  );

  const CapabilityCards = ({ cards }) => (
    <div className="flex flex-wrap gap-3 mb-6 mx-[15%]">
      {cards.map((card) => (
        <CapabilityCard key={card.label} {...card} />
      ))}
    </div>
  );

  const KeyAdvantages = ({advantages}) => (
    <div className="rounded-xl border border-gray-100 dark:border-gray-800 mx-[15%] p-5" style={{ background: theme.bg}}>
      <p className="text-md font-medium uppercase text-center text-gray-400 mb-4 dark:text-gray-500">
        Key advantages
      </p>
      <div className="flex flex-wrap justify-center gap-2.5">
        {advantages.map((advantage) => (
          <div
            key={advantage}
            className="flex items-center gap-2 text-sm text-gray-800 dark:text-gray-200 flex-1 sm:min-w-[35%] min-w-[70%]"
          >
          <span className="flex h-4.5 w-4.5 shrink-0 items-center justify-center rounded-full bg-green-50 dark:bg-green-950">
            < Check className="h-2.5 w-2.5 stroke-green-600 dark:stroke-green-400" strokeWidth={2.5} />
          </span>
            {advantage}
          </div>
        ))}
      </div>
    </div>
  );


  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">

      {/* ---------- HERO ---------- */}
      <section className="hero py-24 bg-linear-to-br from-blue-900 to-black text-white">
        <div className="hero-content text-center max-w-4xl">
          <div>
            <h1 className="text-5xl font-bold mb-6">Features</h1>
            <p className="text-xl opacity-90">
             SecuriVA is an all-in-one AI-powered platform designed to transform the way businesses operate.
              From intelligent virtual agents to enterprise-grade cybersecurity and VPN access, every feature
               is built for efficiency, safety, and compliance.
            </p>
          </div>
        </div>
      </section>

      {/* AI Assistant */}
      <section class="relative overflow-hidden px-8 py-12">

        <h2 class="text-4xl font-normal text-center text-gray-900 mb-2 dark:text-white">
          AI-Powered Voice Assistant <br/> for <span class="italic text-blue-600 dark:text-blue-400">Smarter Business</span> Communication
        </h2>

        <p class="text-[15px] font-light text-gray-500 mb-8 text-center dark:text-gray-400 mx-[15%]">
          SecuriVA's AI-driven voice assistant that automates calls, manages schedules, and connects seamlessly across your entire communication stack.
        </p>

        <div class="border-t border-gray-100 mb-8 dark:border-gray-800"></div>

        <CapabilityCards cards={
          [
            {
              icon: Phone,
              label: "Customer call management",
              description: "Handles calls, inquiries, and follow-ups automatically",
            },
            {
              icon: Calendar,
              label: "Scheduling & calendars",
              description: "Books appointments and manages calendars in real time",
            },
            {
              icon: MessageCircle,
              label: "Multichannel interaction",
              description: "Operates across voice, chat, and digital platforms",
            },
            {
              icon: Zap,
              label: "Seamless integrations",
              description: "Connects with CRMs, cloud platforms, and APIs",
            },
          ]
        }/>

        <KeyAdvantages advantages={[
            "Personalized customer interactions",
            "24/7 availability",
            "Scalable across departments & industries",
            "Embedded cybersecurity for safe voice comms",
          ]
        }/>

      </section>

        {/* Cybersecurity */}
      <section className="relative overflow-hidden px-8 py-12">
        <h2 className="text-4xl font-normal text-center text-gray-900 mb-2 dark:text-white">
          Protect Your Data, Workflows, <br/> and <span className="italic text-blue-600 dark:text-blue-400">Communications</span>
        </h2>
        <p className="text-[15px] font-light text-gray-500 mb-8 text-center dark:text-gray-400 mx-[15%]">
          SecuriVA's cybersecurity module delivers real-time threat detection, encryption, and regulatory compliance.
        </p>
        <div className="border-t border-gray-100 mb-8 dark:border-gray-800"></div>
        <CapabilityCards cards={[
          {
            icon: Activity,
            label: "Continuous monitoring",
            description: "Continuous monitoring and threat prevention",
          },
          {
            icon: Lock,
            label: "Encrypted storage",
            description: "Encrypted data storage and secure communications",
          },
          {
            icon: ShieldCheck,
            label: "Regulatory compliance",
            description: "Compliance with GDPR, HIPAA, PCI-DSS standards",
          },
          {
            icon: Server,
            label: "Vulnerability testing",
            description: "Vulnerability testing and SIEM frameworks for enterprise-grade protection",
          },
        ]}/>
        <KeyAdvantages advantages={[
          "Integrated into all SecuriVA features",
          "Proactive AI-driven threat detection",
          "Regulatory compliance ready",
          "Confidence for highly regulated industries",
        ]}/>
      </section>

      {/* Text AI Agent */}
      <section className="relative overflow-hidden px-8 py-12">
        <h2 className="text-4xl font-normal text-center text-gray-900 mb-2 dark:text-white">
          Intelligent Automation for Email, <br/> Chat, and <span className="italic text-blue-600 dark:text-blue-400">Messaging</span>
        </h2>
        <p className="text-[15px] font-light text-gray-500 mb-8 text-center dark:text-gray-400 mx-[15%]">
          The Text AI Agent enhances business communication by automating key workflows across your entire messaging stack.
        </p>
        <div className="border-t border-gray-100 mb-8 dark:border-gray-800"></div>
        <CapabilityCards cards={[
          {
            icon: Mail,
            label: "Email automation",
            description: "Email responses and follow-ups handled automatically",
          },
          {
            icon: MessageSquare,
            label: "Chat interactions",
            description: "Chat automation on WhatsApp, Gmail, and websites",
          },
          {
            icon: FileText,
            label: "Document handling",
            description: "Document analysis and data extraction at scale",
          },
          {
            icon: Workflow,
            label: "API task automation",
            description: "API-based task automation across platforms",
          },
        ]}/>
        <KeyAdvantages advantages={[
          "Reduces manual workloads",
          "Improves customer response times",
          "Integrates with workflow automation tools",
          "Secure and compliant with data privacy standards",
        ]}/>
      </section>

      {/* VPN */}
      <section className="relative overflow-hidden px-8 py-12">
        <h2 className="text-4xl font-normal text-center text-gray-900 mb-2 dark:text-white">
          Secure, Encrypted, and <br/> <span className="italic text-blue-600 dark:text-blue-400">Compliance-Ready</span> Network Access
        </h2>
        <p className="text-[15px] font-light text-gray-500 mb-8 text-center dark:text-gray-400 mx-[15%]">
          SecuriVA's VPN Secure Access ensures all business communication and automation occurs in a protected, encrypted tunnel.
        </p>
        <div className="border-t border-gray-100 mb-8 dark:border-gray-800"></div>
        <CapabilityCards cards={[
          {
            icon: MousePointerClick,
            label: "One-click secure browsing",
            description: "Secure browsing for calls, texts, emails, and APIs in one click",
          },
          {
            icon: ShieldAlert,
            label: "AI threat detection",
            description: "AI-driven threat detection within VPN traffic",
          },
          {
            icon: Network,
            label: "Adaptive routing",
            description: "Selects the fastest and safest server automatically",
          },
          {
            icon: KeyRound,
            label: "Multi-factor authentication",
            description: "MFA enforcement for all sensitive access points",
          },
        ]}/>
        <KeyAdvantages advantages={[
          "Eliminates the need for separate VPN subscriptions",
          "Embedded into all SecuriVA workflows",
          "Provides enterprise-grade network protection",
          "Supports remote, hybrid, and distributed teams",
        ]}/>
      </section>


      <Sponsors className="bg-white mt-10 pt-5 text-center text-black text-3xl"/>
    </div>
  );
}