import { Link } from "react-router-dom";
import Sponsors from "../components/Sponsors";
import { Check, Phone, Calendar, MessageCircle, Zap, Activity, Lock, ShieldCheck, Server, Mail, MessageSquare, FileText, Workflow, MousePointerClick, ShieldAlert, Network, KeyRound, Layers, Globe, Settings, SlidersHorizontal, BadgeCheck, Play, BookOpen, ChevronRight } from "lucide-react";
import CapabilityCard from "../components/CapabilityCard";
import SymmetricalChecklist from "../components/SymmetricalChecklist";

export default function Features() {

  const CapabilityCards = ({ cards }) => (
    <div className="flex flex-wrap gap-3 mb-6 mx-[15%]">
      {cards.map((card) => (
        <CapabilityCard className="sm:min-w-[35%] min-w-[70%]" key={card.label} {...card} />
      ))}
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
      <section id="virtual-agent" class="relative overflow-hidden px-8 py-12">

        <h2 class="text-4xl font-normal text-center text-gray-900 mb-2 dark:text-white">
          Virtual AI Agent
        </h2>

        <p class="text-xl font-light text-gray-500 mb-8 text-center dark:text-gray-400 mx-[15%]">
          AI-Powered Voice Assistant for Smarter Business Communication
        </p>

        <div class="border-t border-gray-100 mb-8 dark:border-gray-800"></div>

        <div className="mx-[15%] pb-5 text-xl">The Virtual Agent is SecuriVA’s AI-driven voice assistant, capable of:</div>

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

        <SymmetricalChecklist className={"mx-[15%]"} heading={"Key Advantages"} items={[
            "Personalized customer interactions",
            "24/7 availability",
            "Scalable across departments & industries",
            "Embedded cybersecurity for safe voice comms",
          ]
        }/>

        <div className="flex justify-center">
          <Link to={"/agent-voice"} >
            <button className="flex justify-center items-center btn bg-blue-900 mt-10">
              More Information
              <ChevronRight />
            </button>
          </Link>
        </div>

      </section>

        {/* Cybersecurity */}
      <section id="cybersecurity" className="relative overflow-hidden px-8 py-12">
        <h2 className="text-4xl font-normal text-center text-gray-900 mb-2 dark:text-white">
          Cybersecurity
        </h2>
        <p className="text-xl font-light text-gray-500 mb-8 text-center dark:text-gray-400 mx-[15%]">
          Protect Your Data, Workflows, and Communications
        </p>
        <div className="border-t border-gray-100 mb-8 dark:border-gray-800"></div>
        <div className="mx-[15%] pb-5 text-xl">SecuriVA’s cybersecurity module delivers real-time threat detection, encryption, and regulatory compliance.</div>
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
        <SymmetricalChecklist className={"mx-[15%]"} heading={"Key Advantages"} items={[
          "Integrated into all SecuriVA features",
          "Proactive AI-driven threat detection",
          "Regulatory compliance ready",
          "Confidence for highly regulated industries",
        ]}/>
      </section>

      {/* Text AI Agent */}
      <section id="text-agent" className="relative overflow-hidden px-8 py-12">
        <h2 className="text-4xl font-normal text-center text-gray-900 mb-2 dark:text-white">
          Text AI Agent
        </h2>
        <p className="text-xl font-light text-gray-500 mb-8 text-center dark:text-gray-400 mx-[15%]">
          Intelligent Automation for Email, Chat, and Messaging
        </p>
        <div className="border-t border-gray-100 mb-8 dark:border-gray-800"></div>

        <div className="mx-[15%] pb-5 text-xl">The Text AI Agent enhances business communication by automating:</div>

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
        <SymmetricalChecklist className={"mx-[15%]"} heading={"Key Advantages"} items={[
          "Reduces manual workloads",
          "Improves customer response times",
          "Integrates with workflow automation tools",
          "Secure and compliant with data privacy standards",
        ]}/>
      </section>

      {/* VPN */}
      <section id="vpn" className="relative overflow-hidden px-8 py-12">
        <h2 className="text-4xl font-normal text-center text-gray-900 mb-2 dark:text-white">
          VPN Secure Access
        </h2>
        <p className="text-xl font-light text-gray-500 mb-8 text-center dark:text-gray-400 mx-[15%]">
          Secure, Encrypted, and Compliance-Ready Network Access
        </p>
        <div className="border-t border-gray-100 mb-8 dark:border-gray-800"></div>

        <div className="mx-[15%] pb-5 xl text-xl">SecuriVA’s VPN Secure Access ensures all business communication and automation occurs in a protected, encrypted tunnel.</div>

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
        <SymmetricalChecklist className={"mx-[15%]"} heading={"Key Advantages"} items={[
          "Eliminates the need for separate VPN subscriptions",
          "Embedded into all SecuriVA workflows",
          "Provides enterprise-grade network protection",
          "Supports remote, hybrid, and distributed teams",
        ]}/>
      </section>

      {/* Recap */}
      <section className="relative overflow-hidden px-8 py-12 mx-[15%]">
        <h2 className="text-4xl font-normal text-center text-gray-900 mb-2 dark:text-white">
          Why SecuriVA Features Stand Out
        </h2>

        <div className="flex flex-wrap justify-center gap-3 mb-6">
          {[
            { icon: Layers,            label: "All-in-One Platform",         description: "Virtual agents, text AI, VPN, and cybersecurity integrated seamlessly." },
            { icon: Globe,             label: "Cross-Industry Applicability", description: "Healthcare, finance, e-commerce, SMBs, education, government, nonprofits, agriculture, and more." },
            { icon: Settings,          label: "Automation + Security",        description: "Designed to both optimize workflows and protect data simultaneously." },
            { icon: SlidersHorizontal, label: "Customizable and Scalable",    description: "Tailor features for any business size or workflow complexity." },
            { icon: BadgeCheck,        label: "Compliance and Peace of Mind", description: "Built-in protection ensures legal and regulatory requirements are always met." },
          ].map((card) => (
            <CapabilityCard
              key={card.label}
              {...card}
              className="sm:min-w-[35%] min-w-[70%] max-w-[50%]"
            />
          ))}
        </div>
      </section>

      {/* Call to Action */}
      <section className="px-8 py-16 text-center">
        <h2 className="text-4xl font-normal text-gray-900 mb-3 dark:text-white">
          Experience the Power of SecuriVA Features
        </h2>
        <p className="text-[15px] font-light text-gray-500 mb-10 max-w-lg mx-auto dark:text-gray-400">
          Empower your business with secure AI-driven automation and customer interaction.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <Link to={"/contact"}>
            <button className="flex items-center gap-2 rounded-xl bg-red-500 px-6 py-3 text-[14px] font-medium text-white transition-colors hover:bg-red-400">
              <Play className="h-4 w-4 fill-white stroke-none" />
              Request a Demo
            </button>
          </Link>
          <button onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })} className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-6 py-3 text-[14px] font-medium text-gray-800 transition-colors hover:border-gray-300 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:hover:border-gray-600 dark:hover:bg-gray-800">
            <BookOpen className="h-4 w-4 stroke-gray-500 dark:stroke-gray-400" strokeWidth={1.5} />
            Learn More About Each Feature
          </button>
          <Link to={"/contact"}>
            <button className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-6 py-3 text-[14px] font-medium text-gray-800 transition-colors hover:border-gray-300 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:hover:border-gray-600 dark:hover:bg-gray-800">
              <Mail className="h-4 w-4 stroke-gray-500 dark:stroke-gray-400" strokeWidth={1.5} />
              Contact Our Team
            </button>
          </Link>
        </div>
      </section>

      <Sponsors className="bg-white mt-10 pt-5 text-center text-black text-3xl"/>
    </div>
  );
}