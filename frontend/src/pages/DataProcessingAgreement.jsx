import {
  BookOpen, Cpu, ShieldCheck, Users, Globe,
  ClipboardList, Bell, Lock, Server, Activity,
  HeartPulse, Mail, ChevronRight
} from "lucide-react";

import SectionDivider from "../components/SectionDivider.jsx";
import SectionHeader from "../components/SectionHeader";
import InfoCard from "../components/InfoCard";
import InfoCards from "../components/InfoCards.jsx";
import BulletList from "../components/BulletList.jsx";
import ProseBlock from "../components/ProseBlock.jsx";

// ─── main page ────────────────────────────────────────────────────────────────

export default function DataProcessingAgreement() {
  return (
    <div className="min-h-screen bg-gray-900">

      {/* ── HERO ── */}
      <section className="hero py-24 bg-linear-to-br from-blue-900 to-black text-white">
        <div className="hero-content text-center max-w-4xl">
          <div>
            <h1 className="text-5xl font-bold mb-6">Data Processing Agreement</h1>
            <p className="text-xl opacity-90">
              This DPA forms part of the Terms of Service and governs all personal data processing activities performed by SecuriVA on behalf of its clients.
            </p>
            <p className="mt-4 text-sm opacity-60">Last Updated: January 1, 2026 &nbsp;·&nbsp; Applies to all SecuriVA Enterprise Clients</p>
          </div>
        </div>
      </section>

      {/* ── 4.1 Definitions ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader title="Definitions" />
        <SectionDivider />
        <InfoCards cards={[
          {
            icon: Users,
            label: "Controller",
            description: "The client organization determining the purposes and means of personal data processing.",
          },
          {
            icon: Cpu,
            label: "Processor",
            description: "SecuriVA (Kimuntu Power Inc.), processing data on behalf of the Controller.",
          },
          {
            icon: BookOpen,
            label: "Data Subject",
            description: "Any identified or identifiable natural person whose personal data is processed.",
          },
          {
            icon: ClipboardList,
            label: "Personal Data",
            description: "Any information relating to an identified or identifiable natural person.",
          },
          {
            icon: Activity,
            label: "Processing",
            description: "Any operation performed on personal data including collection, storage, use, transfer, and deletion.",
          },
          {
            icon: Server,
            label: "Sub-Processor",
            description: "Third parties engaged by SecuriVA to assist in data processing activities.",
          },
          {
            icon: Bell,
            label: "Security Incident",
            description: "Any confirmed or reasonably suspected breach of security affecting personal data.",
          },
        ]} />
      </section>

      {/* ── 4.2 Scope and Purpose ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="Scope and Purpose of Processing"
          subtitle="SecuriVA processes personal data exclusively on documented instructions from the Controller. Processing activities include:"
        />
        <SectionDivider />
        <BulletList items={[
          "Automation of client-defined workflows and tasks",
          "Management of customer communications (voice, email, chat, video)",
          "Cybersecurity threat monitoring and incident response",
          "Data storage, backup, and disaster recovery operations",
        ]} />
        <p className="mx-[15%] text-lg text-gray-400 font-light">
          SecuriVA will not process data for its own independent purposes without explicit written authorization from the Controller.
        </p>
      </section>

      {/* ── 4.3 Processor Obligations ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="Processor Obligations"
          subtitle="SecuriVA commits to:"
        />
        <SectionDivider />
        <BulletList items={[
          "Process personal data only in accordance with the Controller's documented instructions",
          "Implement and maintain appropriate technical and organizational security measures",
          "Ensure that all authorized personnel are bound by confidentiality obligations",
          "Assist the Controller in fulfilling data subject rights requests under GDPR and applicable law",
          "Notify the Controller of any personal data breach within 72 hours of becoming aware",
          "Upon termination of services, securely delete or return all personal data as directed",
          "Maintain records of all processing activities as required by GDPR Article 30",
        ]} />
      </section>

      {/* ── 4.4 Sub-Processing ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="Sub-Processing"
          subtitle="SecuriVA may engage sub-processors (cloud infrastructure providers, payment processors, communication API providers) subject to:"
        />
        <SectionDivider />
        <BulletList items={[
          "Sub-processors being bound by equivalent data protection obligations",
          "Prior written notification to the Controller of any intended new sub-processors",
          "The Controller retaining the right to reasonably object to new sub-processors",
          "A current list of approved sub-processors available upon request at privacy@securiva.io",
        ]} />
      </section>

      {/* ── 4.5 Security Measures ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="Security Measures"
          subtitle="SecuriVA maintains the following technical and organizational security measures:"
        />
        <SectionDivider />
        <BulletList items={[
          "AES-256 encryption for all data in transit (TLS 1.3) and at rest",
          "Strict Role-Based Access Control (RBAC) with principle of least privilege",
          "Continuous SIEM monitoring for security events and anomaly detection",
          "Annual penetration testing by qualified independent security professionals",
          "Documented incident response procedures with defined escalation paths",
          "Regular security awareness training for all personnel with data access",
        ]} />
      </section>

      {/* ── 4.6 Data Breach Notification ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader title="Data Breach Notification" />
        <SectionDivider />
        <ProseBlock>
          In the event of a confirmed personal data breach, SecuriVA shall notify the Controller without undue delay and within 72 hours where feasible. Breach notifications will include: nature and scope of the breach, categories and approximate number of affected data subjects, likely consequences, and mitigation measures taken or proposed.
        </ProseBlock>
      </section>

      {/* ── 4.7 International Data Transfers ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader title="International Data Transfers" />
        <SectionDivider />
        <ProseBlock>
          Any transfer of personal data outside the EU/EEA or Controller's primary jurisdiction will be protected by: Standard Contractual Clauses (SCCs) approved by the European Commission, adequacy decisions where applicable, and equivalent protective measures compliant with local data protection laws.
        </ProseBlock>
      </section>

      {/* ── 4.8 Audit Rights ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="Audit Rights"
        />
        <SectionDivider />
        <ProseBlock>
          The Controller has the right to audit SecuriVA's data processing activities upon reasonable written notice. SecuriVA will provide: relevant documentation and compliance certifications (SOC 2, ISO 27001, PCI-DSS), access to authorized representatives for documented queries, and cooperation with regulatory inspections as required by law.
        </ProseBlock>
      </section>

      {/* ── 4.9 HIPAA Business Associate Provisions ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader title="HIPAA Business Associate Provisions" />
        <SectionDivider />
        <ProseBlock>
          Where SecuriVA processes Protected Health Information (PHI) on behalf of Covered Entities, it acts as a Business Associate under HIPAA. A separate Business Associate Agreement (BAA) will be executed, incorporating all required HIPAA Privacy Rule and Security Rule safeguards.
        </ProseBlock>
      </section>

      {/* ── 4.10 Contact ── */}
      <section className="px-8 py-16 text-center">
        <h2 className="text-4xl font-normal mb-3 text-white">
          DPA Inquiries & Sub-Processor Requests
        </h2>
        <p className="text-[15px] font-light mb-10 max-w-lg mx-auto text-gray-400">
          For all Data Processing Agreement inquiries and sub-processor requests, please contact our privacy team directly.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <a href="mailto:privacy@securiva.io">
            <button className="flex items-center gap-2 rounded-xl bg-blue-900 px-6 py-3 text-[14px] font-medium text-white transition-colors hover:bg-blue-800">
              <Mail className="h-4 w-4" />
              DPA Inquiries — privacy@securiva.io
            </button>
          </a>
        </div>
        <p className="mt-6 text-xs text-gray-600">
          SecuriVA — Kimuntu Power Inc., Ontario, Canada
        </p>
      </section>

    </div>
  );
}
