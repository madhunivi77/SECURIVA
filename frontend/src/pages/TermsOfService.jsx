import {
  Bot, Workflow, Shield, Network, MessageSquare, BadgeCheck,
  UserCheck, Ban, CreditCard, Cpu, Clock, FileText,
  Scale, Gavel, TriangleAlert, Mail, ChevronRight
} from "lucide-react";

import SectionDivider from "../components/SectionDivider";
import SectionHeader from "../components/SectionHeader";
import InfoCard from "../components/InfoCard";
import InfoCards from "../components/InfoCards";
import BulletList from "../components/BulletList";
import ProseBlock from "../components/ProseBlock";

// ─── main page ────────────────────────────────────────────────────────────────

export default function TermsOfService() {
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">

      {/* ── HERO ── */}
      <section className="hero py-24 bg-linear-to-br from-blue-900 to-black text-white">
        <div className="hero-content text-center max-w-4xl">
          <div>
            <h1 className="text-5xl font-bold mb-6">Terms of Service</h1>
            <p className="text-xl opacity-90">
              By creating an account, accessing, or using SecuriVA, you agree to be legally bound by these Terms of Service. Please read them carefully.
            </p>
            <p className="mt-4 text-sm opacity-60">Last Updated: January 1, 2026 &nbsp;·&nbsp; Effective Date: January 1, 2026</p>
          </div>
        </div>
      </section>

      {/* ── 3.1 Acceptance of Terms ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader title="Acceptance of Terms" />
        <SectionDivider />
        <ProseBlock>
          By accessing or using the SecuriVA platform, you agree to comply with these Terms, our Privacy Policy, Data Processing Agreement, and all applicable policies. If you access the platform on behalf of an organization, you represent that you have authority to bind that entity to these Terms.
        </ProseBlock>
      </section>

      {/* ── 3.2 Description of Services ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="Description of Services"
          subtitle="SecuriVA provides the following core services:"
        />
        <SectionDivider />
        <InfoCards cards={[
          {
            icon: Bot,
            label: "AI Virtual Agent (Voice & Text)",
            description: "Autonomous, human-like interaction capabilities across all communication channels.",
          },
          {
            icon: Workflow,
            label: "Business Automation",
            description: "Intelligent workflow automation integrating with email, CRM, APIs, and third-party platforms.",
          },
          {
            icon: Shield,
            label: "Cybersecurity Engine",
            description: "Real-time AI-driven threat detection, encryption, and compliance monitoring.",
          },
          {
            icon: Network,
            label: "VPN Secure Access",
            description: "Enterprise-grade encrypted network connectivity with zero-trust enforcement.",
          },
          {
            icon: MessageSquare,
            label: "Customer Interaction Tools",
            description: "Multi-channel engagement across voice, text, chat, email, and video.",
          },
          {
            icon: BadgeCheck,
            label: "Data Protection & Compliance",
            description: "Automated compliance management for GDPR, HIPAA, PCI-DSS, and other standards.",
          },
        ]} />
        <p className="mx-[15%] text-lg text-gray-500 dark:text-gray-400 font-light">
          SecuriVA reserves the right to update, modify, enhance, or discontinue any aspect of the service with reasonable notice to users.
        </p>
      </section>

      {/* ── 3.3 Eligibility ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader title="Eligibility" />
        <SectionDivider />
        <ProseBlock>
          Users must be at least 18 years of age and legally capable of entering binding contracts. By using SecuriVA, you confirm these requirements are met.
        </ProseBlock>
      </section>

      {/* ── 3.4 Account Registration & Security ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="Account Registration & Security"
        />
        <SectionDivider />
        <BulletList items={[
          "Provide accurate, current, and complete registration information",
          "Maintain the confidentiality of your account credentials at all times",
          "Immediately notify SecuriVA of any unauthorized access or suspected breach at security@securiva.com",
          "Accept responsibility for all activities conducted under your account",
          "Not share account credentials with unauthorized personnel",
        ]} />
      </section>

      {/* ── 3.5 Acceptable Use Policy ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="Acceptable Use Policy"
          subtitle="You agree not to use the SecuriVA platform for:"
        />
        <SectionDivider />
        <BulletList items={[
          "Illegal, fraudulent, harmful, or deceptive activities",
          "Unauthorized data collection, surveillance, or privacy violations",
          "Spamming, phishing, or unsolicited commercial messaging",
          "Uploading, distributing, or executing viruses, malware, or malicious code",
          "Infringing upon intellectual property rights of any party",
          "Automating activities that violate third-party platform policies (Gmail, WhatsApp, Salesforce, etc.)",
          "Attempting to circumvent platform security, reverse-engineer the platform, or access unauthorized systems",
          "Using the platform to harm, harass, or discriminate against individuals or groups",
        ]} />
        <p className="mx-[15%] text-lg text-gray-500 dark:text-gray-400 font-light">
          Violations may result in immediate account suspension or termination, without refund, and may be reported to appropriate authorities.
        </p>
      </section>

      {/* ── 3.6 Payment & Billing ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="Payment & Billing"
        />
        <SectionDivider />
        <BulletList items={[
          "Subscription fees and payment terms are detailed in the applicable Pricing Policy",
          "All payments are processed through PCI-DSS certified payment gateways",
          "Fees are non-refundable unless otherwise required by applicable law",
          "Failure to maintain payment may result in service suspension after reasonable notice",
          "Applicable taxes and processing fees are the responsibility of the subscriber",
          "Enterprise clients may negotiate custom billing terms within their service agreements",
        ]} />
      </section>

      {/* ── 3.7 Intellectual Property ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="Intellectual Property"
        />
        <SectionDivider />
        <BulletList items={[
          "All platform software, algorithms, AI models, designs, brand assets, and documentation are the exclusive intellectual property of SecuriVA and Kimuntu Power Inc.",
          "Users may not copy, reverse-engineer, disassemble, or distribute SecuriVA software without explicit written authorization",
          "Users retain full ownership of their data, uploaded content, and customized workflow configurations",
          "SecuriVA is granted a limited, non-exclusive license to process user data solely for platform functionality",
        ]} />
      </section>

      {/* ── 3.8 Service Availability & SLA ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="Service Availability & SLA"
          subtitle="SecuriVA targets 99.9% platform uptime. In the event of planned maintenance or unforeseen outages:"
        />
        <SectionDivider />
        <BulletList items={[
          "Advance notice will be provided for scheduled maintenance windows where possible",
          "SecuriVA is not liable for service interruptions caused by third-party provider failures, force majeure events, or factors outside reasonable control",
          "Enterprise clients may negotiate specific Service Level Agreements (SLAs) with defined uptime guarantees and remedies",
        ]} />
      </section>

      {/* ── 3.9 Disclaimer of Warranties ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader title="Disclaimer of Warranties" />
        <SectionDivider />
        <ProseBlock>
          The SecuriVA platform is provided on an 'as is' and 'as available' basis. SecuriVA makes no warranties, express or implied, including but not limited to implied warranties of merchantability, fitness for a particular purpose, or non-infringement, to the maximum extent permitted by applicable law.
        </ProseBlock>
      </section>

      {/* ── 3.10 Limitation of Liability ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader title="Limitation of Liability" />
        <SectionDivider />
        <ProseBlock>
          To the maximum extent permitted by law: (a) SecuriVA is not liable for any indirect, incidental, special, consequential, or punitive damages; (b) SecuriVA's total aggregate liability for any claims shall not exceed the total fees paid by the user in the twelve (12) months preceding the claim; (c) these limitations apply regardless of the legal theory of the claim.
        </ProseBlock>
      </section>

      {/* ── 3.11 Indemnification ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader title="Indemnification" />
        <SectionDivider />
        <ProseBlock>
          You agree to indemnify, defend, and hold harmless SecuriVA, Kimuntu Power Inc., and their respective officers, directors, employees, and affiliates from any claims, liabilities, damages, costs, and expenses (including reasonable legal fees) arising from: (a) your use or misuse of the platform; (b) your violation of these Terms; (c) your violation of any third-party rights or applicable laws.
        </ProseBlock>
      </section>

      {/* ── 3.12 Termination ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader title="Termination" />
        <SectionDivider />
        <ProseBlock>
          SecuriVA may suspend or permanently terminate your account, with or without prior notice, if you breach these Terms, fail to pay applicable fees, misuse platform integrations, or engage in conduct harmful to other users or the platform. Upon termination, your right to access the platform ceases immediately.
        </ProseBlock>
      </section>

      {/* ── 3.13 Governing Law ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="Governing Law & Dispute Resolution"
        />
        <SectionDivider />
        <ProseBlock>
          These Terms are governed by and construed in accordance with the laws of Ontario, Canada, without regard to conflict of law principles. Any disputes shall first be subject to good-faith negotiation, and if unresolved, shall be submitted to binding arbitration or the courts of Ontario, Canada.
        </ProseBlock>
      </section>

      {/* ── 3.14 Contact ── */}
      <section className="px-8 py-16 text-center">
        <h2 className="text-4xl font-normal text-gray-900 mb-3 dark:text-white">
          Legal Inquiries & Contact
        </h2>
        <p className="text-[15px] font-light text-gray-500 mb-10 max-w-lg mx-auto dark:text-gray-400">
          For legal matters or general questions about these Terms, please reach out to our team directly.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <a href="mailto:legal@securiva.io">
            <button className="flex items-center gap-2 rounded-xl bg-blue-900 px-6 py-3 text-[14px] font-medium text-white transition-colors hover:bg-blue-800">
              <Gavel className="h-4 w-4" />
              Legal Inquiries — legal@securiva.io
            </button>
          </a>
          <a href="mailto:contact@securiva.io">
            <button className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-6 py-3 text-[14px] font-medium text-gray-800 transition-colors hover:border-gray-300 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:hover:border-gray-600 dark:hover:bg-gray-800">
              <Mail className="h-4 w-4 stroke-gray-500 dark:stroke-gray-400" strokeWidth={1.5} />
              General — contact@securiva.io
            </button>
          </a>
        </div>
        <p className="mt-6 text-xs text-gray-400 dark:text-gray-600">
          SecuriVA — Kimuntu Power Inc., Ontario, Canada
        </p>
      </section>

    </div>
  );
}
