import {
  ShieldCheck, Settings, BarChart2, Lock, Globe, Mail, ChevronRight
} from "lucide-react";

import SectionDivider from "../components/SectionDivider";
import SectionHeader from "../components/SectionHeader";
import ProseBlock from "../components/ProseBlock";

// ─── small reusable components ────────────────────────────────────────────────

function CookieTable({ rows }) {
  return (
    <div className="mx-[15%] mb-6 overflow-x-auto rounded-xl border border-gray-700">
      <table className="w-full text-lg">
        <thead>
          <tr className="bg-blue-900 text-white">
            <th className="text-left px-5 py-3 font-medium w-1/4">Type</th>
            <th className="text-left px-5 py-3 font-medium">Purpose</th>
            <th className="text-left px-5 py-3 font-medium w-1/4">Can Be Disabled?</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(({ type, purpose, canDisable, icon: Icon }, i) => (
            <tr key={type} className={i % 2 === 0 ? "bg-gray-800" : "bg-gray-850"}>
              <td className="px-5 py-4">
                <div className="flex items-center gap-2">
                  <Icon className="h-4 w-4 text-blue-400 shrink-0" strokeWidth={1.5} />
                  <span className="font-medium text-white">{type}</span>
                </div>
              </td>
              <td className="px-5 py-4 text-gray-300">{purpose}</td>
              <td className="px-5 py-4 text-gray-300">{canDisable}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ─── main page ────────────────────────────────────────────────────────────────

export default function CookiePolicy() {
  const cookieRows = [
    {
      icon: ShieldCheck,
      type: "Strictly Necessary",
      purpose: "Authentication, session management, security",
      canDisable: "No — required for platform operation",
    },
    {
      icon: Settings,
      type: "Functional",
      purpose: "User preferences, language settings, personalization",
      canDisable: "Yes — may limit some features",
    },
    {
      icon: BarChart2,
      type: "Analytics",
      purpose: "Anonymized usage data, performance metrics",
      canDisable: "Yes — platform still functions fully",
    },
    {
      icon: Lock,
      type: "Security",
      purpose: "Fraud detection, threat monitoring, audit logs",
      canDisable: "No — required for compliance",
    },
  ];

  return (
    <div className="min-h-screen bg-gray-900">

      {/* ── HERO ── */}
      <section className="hero py-24 bg-linear-to-br from-blue-900 to-black text-white">
        <div className="hero-content text-center max-w-4xl">
          <div>
            <h1 className="text-5xl font-bold mb-6">Cookie Policy</h1>
            <p className="text-xl opacity-90">
              SecuriVA uses cookies and similar tracking technologies to ensure the platform operates correctly, improve user experience, and analyze platform performance.
            </p>
            <p className="mt-4 text-sm opacity-60">Last Updated: January 1, 2026</p>
          </div>
        </div>
      </section>

      {/* ── 5.1 Types of Cookies Used ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader title="Types of Cookies Used" />
        <SectionDivider />
        <CookieTable rows={cookieRows} />
      </section>

      {/* ── 5.2 Managing Cookies ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader title="Managing Cookies" />
        <SectionDivider />
        <ProseBlock>
          You may manage cookie preferences through your browser settings or the SecuriVA cookie consent manager available at platform login. Disabling strictly necessary or security cookies may impair platform functionality and security capabilities.
        </ProseBlock>
      </section>

      {/* ── 5.3 Third-Party Cookies ── */}
      <section className="relative overflow-hidden px-8 py-12">
        <SectionHeader title="Third-Party Cookies" />
        <SectionDivider />
        <ProseBlock>
          Integrated third-party services (analytics providers, payment processors, communication platforms) may set their own cookies subject to their respective privacy policies. SecuriVA does not control these third-party cookies.
        </ProseBlock>
      </section>

      {/* ── Contact ── */}
      <section className="px-8 py-16 text-center">
        <h2 className="text-4xl font-normal mb-3 text-white">
          Questions About Cookies?
        </h2>
        <p className="text-[15px] font-light mb-10 max-w-lg mx-auto text-gray-400">
          For any questions about how SecuriVA uses cookies and tracking technologies, reach out to our privacy team.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <a href="mailto:privacy@securiva.io">
            <button className="flex items-center gap-2 rounded-xl bg-blue-900 px-6 py-3 text-[14px] font-medium text-white transition-colors hover:bg-blue-800">
              <Mail className="h-4 w-4" />
              Contact — privacy@securiva.io
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
