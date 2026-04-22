import {
  Network, Layers, Activity, ShieldCheck,
  KeyRound, Lock, Code2, Wifi,
  ScanSearch, FlaskConical, Timer, Megaphone, Bug,
  Bell, PackageSearch, RotateCcw, Globe, ClipboardList,
  Database, Server, BookOpen, Mail, ChevronRight
} from "lucide-react";

import SectionDivider from "../components/SectionDivider";
import SectionHeader from "../components/SectionHeader";
import InfoCard from "../components/InfoCard";
import InfoCards from "../components/InfoCards";
import BulletList from "../components/BulletList";
import ProseBlock from "../components/ProseBlock";

// ─── main page ────────────────────────────────────────────────────────────────

export default function SecurityPolicy() {
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">

      {/* ── HERO ── */}
      <section className="hero py-24 bg-linear-to-br from-blue-900 to-black text-white">
        <div className="hero-content text-center max-w-4xl">
          <div>
            <h1 className="text-5xl font-bold mb-6">Security Policy</h1>
            <p className="mt-4 text-sm opacity-60">Last Updated: January 1, 2026 &nbsp;·&nbsp; Classification: Public</p>
          </div>
        </div>
      </section>

      {/* ── 6.1 Security Framework ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader
          title="Security Framework"
          subtitle="SecuriVA's security architecture is built on zero-trust principles, ensuring that all users, devices, and network traffic are continuously verified regardless of location or prior authorization. Key framework components include:"
        />
        <SectionDivider />
        <InfoCards cards={[
          {
            icon: Network,
            label: "Zero-Trust Network Architecture",
            description: "No implicit trust granted based on network location.",
          },
          {
            icon: Layers,
            label: "Defense-in-Depth",
            description: "Multiple independent security layers providing redundant protection.",
          },
          {
            icon: Activity,
            label: "Continuous Monitoring",
            description: "Real-time threat detection and automated response capabilities.",
          },
          {
            icon: ShieldCheck,
            label: "Compliance-by-Design",
            description: "Security controls embedded in all platform components from inception.",
          },
        ]} />
      </section>

      {/* ── 6.2 Access Control ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader title="Access Control" />
        <SectionDivider />
        <BulletList items={[
          "Multi-factor authentication (MFA) required for all administrative and privileged access",
          "Role-Based Access Control (RBAC) with principle of least privilege enforced",
          "Regular access reviews and automatic deprovisioning for inactive accounts",
          "Privileged Access Management (PAM) controls for sensitive system access",
        ]} />
      </section>

      {/* ── 6.3 Encryption Standards ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader title="Encryption Standards" />
        <SectionDivider />
        <InfoCards cards={[
          {
            icon: Lock,
            label: "Data in Transit",
            description: "TLS 1.3 with perfect forward secrecy for all communications.",
          },
          {
            icon: Database,
            label: "Data at Rest",
            description: "AES-256 encryption for all stored data and backups.",
          },
          {
            icon: Code2,
            label: "API Communications",
            description: "Encrypted via OAuth 2.0 with signed JWT tokens.",
          },
          {
            icon: Wifi,
            label: "VPN Tunnels",
            description: "Enterprise-grade encrypted connectivity for all remote access.",
          },
        ]} />
      </section>

      {/* ── 6.4 Vulnerability Management ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader title="Vulnerability Management" />
        <SectionDivider />
        <BulletList items={[
          "Continuous automated vulnerability scanning of all platform components",
          "Annual independent penetration testing by certified security professionals",
          "Patch management policy requiring critical patches within 72 hours of release",
          "Responsible disclosure program for external security researchers",
          "Bug bounty program available — contact: security@securiva.io",
        ]} />
      </section>

      {/* ── 6.5 Incident Response ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader title="Incident Response" />
        <SectionDivider />
        <ProseBlock>
          SecuriVA maintains a documented Incident Response Plan including: incident detection and classification, containment and eradication procedures, recovery and post-incident analysis, regulatory notification within required timeframes (72 hours for GDPR), and lessons-learned documentation to prevent recurrence.
        </ProseBlock>
      </section>

      {/* ── 6.6 Business Continuity ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader title="Business Continuity" />
        <SectionDivider />
        <BulletList items={[
          "Daily encrypted backups with one-click restoration capability",
          "Geo-redundant cloud infrastructure across multiple availability zones",
          "Disaster recovery plan with defined Recovery Time Objective (RTO) and Recovery Point Objective (RPO)",
          "Regular business continuity testing and tabletop exercises",
        ]} />
      </section>

      {/* ── 6.7 Responsible Disclosure ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader title="Responsible Disclosure" />
        <SectionDivider />
        <ProseBlock>
          If you discover a potential security vulnerability in SecuriVA, please report it responsibly to: security@securiva.io. We commit to acknowledging reports within 48 hours and providing status updates throughout the remediation process.
        </ProseBlock>
      </section>

      {/* ── Contact ── */}
      <section className="px-8 py-16 text-center">
        <h2 className="text-4xl font-normal text-gray-900 mb-3 dark:text-white">
          Report a Security Issue
        </h2>
        <p className="text-[15px] font-light text-gray-500 mb-10 max-w-lg mx-auto dark:text-gray-400">
          Discovered a potential vulnerability? Reach out to our security team directly. We commit to acknowledging all reports within 48 hours.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <a href="mailto:security@securiva.io">
            <button className="flex items-center gap-2 rounded-xl bg-blue-900 px-6 py-3 text-[14px] font-medium text-white transition-colors hover:bg-blue-800">
              <Mail className="h-4 w-4" />
              Security — security@securiva.io
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
