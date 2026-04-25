import {
  Shield, Eye, Database, Share2, Clock, UserCheck,
  HeartPulse, CreditCard, Cookie, Globe, Mail,
  Lock, Server, ShieldCheck, Activity, KeyRound,
  ChevronRight
} from "lucide-react";

import SectionDivider from "../components/SectionDivider";
import SectionHeader from "../components/SectionHeader";
import InfoCard from "../components/InfoCard";
import InfoCards from "../components/InfoCards";
import BulletList from "../components/BulletList";
import ComplianceBadge from "../components/ComplianceBadge";

// ─── small reusable components ────────────────────────────────────────────────

function RightsTable({ rights }) {
  return (
    <div className="mx-[15%] mb-6 overflow-x-auto rounded-xl border border-gray-200 dark:border-gray-700">
      <table className="w-full text-lg">
        <thead>
          <tr className="bg-blue-900 text-white">
            <th className="text-left px-5 py-3 font-medium w-1/3">Right</th>
            <th className="text-left px-5 py-3 font-medium">Description</th>
          </tr>
        </thead>
        <tbody>
          {rights.map(({ right, description }, i) => (
            <tr
              key={right}
              className={
                i % 2 === 0
                  ? "bg-gray-800"
                  : "bg-gray-850"
              }
            >
              <td className="px-5 py-3 font-medium text-gray-900 dark:text-white">{right}</td>
              <td className="px-5 py-3 text-gray-600 dark:text-gray-400">{description}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ─── main page ────────────────────────────────────────────────────────────────

export default function PrivacyPolicy() {
  const rights = [
    { right: "Right of Access",           description: "Request a copy of your personal data we hold" },
    { right: "Right to Rectification",    description: "Request correction of inaccurate or incomplete data" },
    { right: "Right to Erasure",          description: "Request deletion of your personal data ('right to be forgotten')" },
    { right: "Right to Restriction",      description: "Request that we limit how we process your data" },
    { right: "Right to Portability",      description: "Receive your data in a structured, machine-readable format" },
    { right: "Right to Object",           description: "Object to processing based on legitimate interests or direct marketing" },
    { right: "Right to Withdraw Consent", description: "Withdraw consent at any time without affecting prior processing" },
  ];

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">

      {/* ── HERO ── */}
      <section className="hero py-24 bg-linear-to-br from-blue-900 to-black text-white">
        <div className="hero-content text-center max-w-4xl">
          <div>
            <h1 className="text-5xl font-bold mb-6">Privacy Policy</h1>
            <p className="text-xl opacity-90">
              SecuriVA is committed to protecting your privacy and handling your personal data
              with the highest standards of security, transparency, and compliance.
            </p>
            <p className="mt-4 text-sm opacity-60">Last Updated: January 1, 2026 &nbsp;·&nbsp; Jurisdiction: Ontario, Canada &nbsp;·&nbsp; Company: SecuriVA (Kimuntu Power Inc.) </p>
          </div>
        </div>
      </section>

      {/* ── 2.1 Information We Collect ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="Information We Collect"
          subtitle="We collect only what's necessary to deliver a secure, high-quality experience."
        />
        <SectionDivider />
        <div className="mx-[15%] pb-5 text-xl text-gray-800 dark:text-gray-200">
          SecuriVA collects three categories of information to power and secure the platform:
        </div>
        <InfoCards cards={[
          {
            icon: UserCheck,
            label: "Information You Provide Directly",
            description: "Account registration details: name, email address, phone number, organization name. Payment and billing information (processed via PCI-DSS certified gateways). Customer data uploaded to the platform: emails, messages, documents, schedules, workflows. Support requests, feedback, and communications submitted to our team.",
          },
          {
            icon: Activity,
            label: "Information Collected Automatically",
            description: "Usage data: platform interactions, automated tasks executed, API requests made. Device and browser information: browser type, operating system, device identifiers. Network data: IP address, session logs, access timestamps. Performance data: response times, error logs, feature usage patterns (anonymized).",
          },
          {
            icon: Globe,
            label: "Third-Party Integration Data",
            description: "When you connect external platforms (Gmail, WhatsApp, Salesforce, Microsoft, banking APIs, etc.), SecuriVA accesses and processes data strictly as authorized by you. We act as a data processor on your behalf for all integrated platform data.",
          },
        ]} />
      </section>

      {/* ── 2.2 How We Use Your Information ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="How We Use Your Information"
          subtitle="Your data is used exclusively to operate, protect, and improve the SecuriVA platform."
        />
        <SectionDivider />
        <BulletList items={[
          "Provide, maintain, and continuously improve the SecuriVA platform",
          "Execute automated workflows and tasks as instructed by you",
          "Facilitate multi-channel communications (voice, email, chat, video)",
          "Detect, prevent, and respond to cybersecurity threats in real time",
          "Ensure ongoing compliance with applicable laws and regulations",
          "Process payments and manage billing relationships",
          "Improve AI models and platform capabilities using only anonymized or aggregated data",
          "Send service notifications, security alerts, and compliance updates",
        ]} />
      </section>

      {/* ── 2.3 Data Security ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="Data Security & Protection"
          subtitle="A comprehensive, multi-layered security architecture protecting every layer of your data."
        />
        <SectionDivider />
        <div className="mx-[15%] pb-5 text-xl text-gray-800 dark:text-gray-200">
          SecuriVA implements industry-leading safeguards at every level:
        </div>
        <InfoCards cards={[
          {
            icon: Lock,
            label: "AES-256 Encryption",
            description: "End-to-end AES-256 encryption for all data in transit and at rest.",
          },
          {
            icon: Shield,
            label: "Zero-Trust Architecture",
            description: "Zero-trust network architecture requiring verification for all access requests.",
          },
          {
            icon: Server,
            label: "SIEM Monitoring",
            description: "Continuous monitoring via Security Information and Event Management (SIEM) systems.",
          },
          {
            icon: KeyRound,
            label: "MFA Enforcement",
            description: "Multi-factor authentication (MFA) enforced on all administrative and sensitive access.",
          },
          {
            icon: ShieldCheck,
            label: "RBAC Controls",
            description: "Role-Based Access Control (RBAC) limiting data access to authorized personnel only.",
          },
          {
            icon: Activity,
            label: "Penetration Testing",
            description: "Regular penetration testing and vulnerability assessments by independent security firms.",
          },
        ]} />
        <p className="mx-[15%] mt-2 text-sm text-gray-500 dark:text-gray-400 italic">
          Important: While SecuriVA employs industry-leading security safeguards, no system can guarantee absolute security. Users are responsible for maintaining secure credentials and access practices on their end.
        </p>
      </section>

      {/* ── 2.4 Data Sharing ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="Data Sharing & Disclosure"
          subtitle="SecuriVA does not sell, rent, or trade your personal data — ever."
        />
        <SectionDivider />
        <div className="mx-[15%] pb-5 text-xl text-gray-800 dark:text-gray-200">
          Data may be shared only under strictly limited conditions:
        </div>
        <BulletList items={[
          "With Your Consent: When you authorize integration with third-party platforms",
          "Trusted Service Providers: Vetted vendors for cloud hosting, payment processing, and cybersecurity monitoring — all bound by equivalent data protection obligations",
          "Legal Obligations: When required by applicable law, valid legal process, or regulatory authority",
          "Business Transfers: In the event of a merger, acquisition, or restructuring, your data may transfer to the successor entity under equivalent protections",
        ]} />
      </section>

      {/* ── 2.5 Data Retention ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="Data Retention"
          subtitle="We retain your data only as long as necessary or required by law."
        />
        <SectionDivider />
        <BulletList items={[
          "Personal data is retained while your account is active or as required by applicable law",
          "You may request deletion of your personal data at any time by contacting privacy@securiva.com",
          "Encrypted backup copies may be retained for a limited period for disaster recovery purposes",
          "Anonymized and aggregated data may be retained indefinitely for platform improvement",
        ]} />
      </section>

      {/* ── 2.6 Your Rights ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="Your Rights"
          subtitle="Depending on your jurisdiction, you hold the following rights over your personal data."
        />
        <SectionDivider />
        <RightsTable rights={rights} />
        <p className="mx-[15%] mt-4 text-sm text-gray-500 dark:text-gray-400">
          To exercise any of these rights, contact:{" "}
          <a href="mailto:privacy@securiva.io" className="text-blue-700 dark:text-blue-400 hover:underline">
            privacy@securiva.io
          </a>
        </p>
      </section>

      {/* ── 2.7 / 2.8 / 2.10 Compliance ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="Regulatory Compliance"
          subtitle="Built from the ground up to meet the world's most demanding compliance frameworks."
        />
        <SectionDivider />
        <div className="flex flex-wrap gap-4 mx-[15%] mb-6">
          <ComplianceBadge
            icon={HeartPulse}
            label="HIPAA Compliance"
            description="For healthcare clients processing Protected Health Information (PHI), SecuriVA acts as a Business Associate under HIPAA and will execute a Business Associate Agreement (BAA). We implement all required administrative, physical, and technical safeguards to protect PHI."
          />
          <ComplianceBadge
            icon={CreditCard}
            label="PCI-DSS Compliance"
            description="All payment processing uses PCI-DSS certified gateways (Stripe, PayPal, or equivalent). SecuriVA does not store, process, or transmit full credit card numbers. Financial transaction data is handled exclusively by compliant certified providers."
          />
          <ComplianceBadge
            icon={Globe}
            label="International Data Transfers"
            description="When data is transferred outside your jurisdiction, SecuriVA ensures protection through Standard Contractual Clauses (SCCs) under GDPR, adequacy decisions where applicable, and equivalent contractual protections complying with local regulations."
          />
        </div>
      </section>

      {/* ── 2.9 Cookies ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="Cookies & Tracking"
          subtitle="We use only the cookies necessary to operate, analyse, and personalize the platform."
        />
        <SectionDivider />
        <InfoCards cards={[
          {
            icon: ShieldCheck,
            label: "Functional Cookies",
            description: "Required for platform operations and authentication sessions.",
          },
          {
            icon: Eye,
            label: "Analytics Cookies",
            description: "Anonymized usage data to improve platform performance.",
          },
          {
            icon: Database,
            label: "Preference Cookies",
            description: "Remember your settings and personalization choices.",
          },
        ]} />
        <p className="mx-[15%] text-sm text-gray-500 dark:text-gray-400">
          You may manage cookie preferences through your browser settings. Disabling functional cookies may limit certain platform features.
        </p>
      </section>

      {/* ── Contact ── */}
      <section className="px-8 py-16 text-center">
        <h2 className="text-4xl font-normal text-gray-900 mb-3 dark:text-white">
          Questions About Your Privacy?
        </h2>
        <p className="text-[15px] font-light text-gray-500 mb-10 max-w-lg mx-auto dark:text-gray-400">
          Our Data Protection Officer is available to address any concerns about how your data is collected, used, or stored.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <a href="mailto:privacy@securiva.io">
            <button className="flex items-center gap-2 rounded-xl bg-blue-900 px-6 py-3 text-[14px] font-medium text-white transition-colors hover:bg-blue-800">
              <Mail className="h-4 w-4" />
              Contact DPO — privacy@securiva.io
            </button>
          </a>
          <a href="mailto:contact@securiva.io">
            <button className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-6 py-3 text-[14px] font-medium text-gray-800 transition-colors hover:border-gray-300 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:hover:border-gray-600 dark:hover:bg-gray-800">
              <Mail className="h-4 w-4 stroke-gray-500 dark:stroke-gray-400" strokeWidth={1.5} />
              General Inquiries — contact@securiva.io
            </button>
          </a>
        </div>
        <p className="mt-6 text-xs text-gray-400 dark:text-gray-600">
          SecuriVA Headquarters — Kimuntu Power Inc., Ontario, Canada
        </p>
      </section>

    </div>
  );
}
