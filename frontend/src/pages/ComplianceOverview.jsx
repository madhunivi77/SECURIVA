import {
  Globe, HeartPulse, CreditCard, BadgeCheck,
  Scale, Lock, Users, FileText, Bell, ClipboardList,
  ShieldCheck, Database, Coins, BarChart2, Mail, ChevronRight
} from "lucide-react";

import SectionDivider from '../components/SectionDivider.jsx';
import SectionHeader from "../components/SectionHeader.jsx";
import InfoCard from "../components/InfoCard.jsx";
import InfoCards from "../components/InfoCards.jsx";
import BulletList from "../components/BulletList.jsx";

// ─── main page ────────────────────────────────────────────────────────────────

export default function ComplianceOverview() {
  return (
    <div className="min-h-screen bg-gray-900">

      {/* ── HERO ── */}
      <section className="hero py-24 bg-linear-to-br from-blue-900 to-black text-white">
        <div className="hero-content text-center max-w-4xl">
          <div>
            <h1 className="text-5xl font-bold mb-6">Compliance Overview</h1>
            <p className="text-xl opacity-90">
              SecuriVA is designed and operated to meet the highest global regulatory standards. This section summarizes our compliance posture across key frameworks.
            </p>
          </div>
        </div>
      </section>

      {/* ── 7.1 GDPR ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="GDPR (General Data Protection Regulation)"
          subtitle="SecuriVA fully complies with the EU General Data Protection Regulation (GDPR) and applicable national implementations:"
        />
        <SectionDivider />
        <BulletList items={[
          "Lawful basis established for all personal data processing activities",
          "Privacy-by-design and data minimization principles embedded in platform architecture",
          "Comprehensive data subject rights management (access, rectification, erasure, portability, objection)",
          "Data Protection Officer (DPO) available at privacy@securiva.io",
          "Standard Contractual Clauses (SCCs) in place for all international data transfers",
          "72-hour breach notification procedures to supervisory authorities",
          "Records of processing activities maintained per Article 30",
        ]} />
      </section>

      {/* ── 7.2 HIPAA ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="HIPAA (Health Insurance Portability and Accountability Act)"
          subtitle="For clients processing Protected Health Information (PHI):"
        />
        <SectionDivider />
        <BulletList items={[
          "Business Associate Agreement (BAA) executed with all qualifying healthcare clients",
          "Administrative, physical, and technical safeguards for PHI as required by HIPAA Security Rule",
          "Minimum necessary standard applied to all PHI access and processing",
          "Audit controls and access logs maintained for all PHI interactions",
          "Breach notification procedures compliant with HIPAA Breach Notification Rule",
        ]} />
      </section>

      {/* ── 7.3 PCI-DSS ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="PCI-DSS (Payment Card Industry Data Security Standard)"
          subtitle="For all payment and financial data processing:"
        />
        <SectionDivider />
        <BulletList items={[
          "PCI-DSS certified payment gateways (Stripe, PayPal) exclusively used for card processing",
          "SecuriVA does not store, process, or transmit full Primary Account Numbers (PANs)",
          "Tokenization applied to all payment references stored in the platform",
          "Annual PCI-DSS compliance assessments and attestation",
        ]} />
      </section>

      {/* ── 7.4 Additional Standards ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="Additional Standards"
          subtitle="SecuriVA aligns with and works toward the following additional frameworks:"
        />
        <SectionDivider />
        <InfoCards cards={[
          {
            icon: ShieldCheck,
            label: "SOC 2 Type II",
            description: "Security, availability, confidentiality, and privacy trust service criteria.",
          },
          {
            icon: Lock,
            label: "ISO 27001",
            description: "Information security management system best practices.",
          },
          {
            icon: Scale,
            label: "CCPA/CPRA",
            description: "California Consumer Privacy Act compliance for US-based users.",
          },
          {
            icon: FileText,
            label: "Canada PIPEDA",
            description: "Personal Information Protection and Electronic Documents Act.",
          },
        ]} />
      </section>

      {/* ── Contact ── */}
      <section className="px-8 py-16 text-center">
        <h2 className="text-4xl font-normal mb-3 text-white">
          Compliance Inquiries
        </h2>
        <p className="text-[15px] font-light mb-10 max-w-lg mx-auto text-gray-400">
          For questions about SecuriVA's compliance posture or to request documentation, reach out to our privacy team.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <a href="mailto:privacy@securiva.io">
            <button className="flex items-center gap-2 rounded-xl bg-blue-900 px-6 py-3 text-[14px] font-medium text-white transition-colors hover:bg-blue-800">
              <Mail className="h-4 w-4" />
              Privacy — privacy@securiva.io
            </button>
          </a>
          <a href="mailto:contact@securiva.io">
            <button className="flex items-center gap-2 rounded-xl border px-6 py-3 text-[14px] font-medium transition-colors border-gray-700 bg-gray-900 text-white hover:border-gray-600 hover:bg-gray-800">
              <Mail className="h-4 w-4 stroke-gray-400" strokeWidth={1.5} />
              General — contact@securiva.io
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
