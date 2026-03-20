// Contact.jsx
import { useState } from "react";

export default function Contact() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    company: "",
    type: "general",
    message: "",
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    alert("Message sent! Our team will contact you shortly.");
    setFormData({
      name: "",
      email: "",
      company: "",
      type: "general",
      message: "",
    });
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">

      {/* ---------- HERO ---------- */}
      <section className="hero py-24 bg-gradient-to-br from-blue-900 to-black text-white">
        <div className="hero-content text-center max-w-4xl">
          <div>
            <h1 className="text-5xl font-bold mb-6">Contact SecuriVA</h1>
            <p className="text-xl opacity-90">
              Our team helps organizations deploy secure AI systems, resolve
              technical issues, and design enterprise solutions. Tell us your
              needs and we’ll respond quickly with expert assistance.
            </p>
          </div>
        </div>
      </section>

      {/* ---------- CONTACT SERVICES ---------- */}
      <section className="relative py-20 px-10 overflow-hidden">

        {/* 🔵 Background Image */}
        <img
          src="/Cybersecurity_Protection.png"
          alt="Cybersecurity Protection"
          className="absolute inset-0 w-full h-full object-cover opacity-60"
        />

        {/* 🎨 Horizontal gradient fade */}
        <div className="absolute inset-0 bg-gradient-to-r from-white via-transparent to-white dark:from-gray-900 dark:via-transparent dark:to-gray-900"></div>

        {/* 🎨 Vertical gradient fade */}
        <div className="absolute inset-0 bg-gradient-to-b from-white via-transparent to-white dark:from-gray-900 dark:via-transparent dark:to-gray-900"></div>

        {/* 🧠 Content */}
        <div className="relative max-w-6xl mx-auto">

          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">
            Contact Services
          </h2>

          <div className="grid md:grid-cols-3 gap-8">

            <div className="card bg-white/90 backdrop-blur dark:bg-gray-800/90 shadow-lg">
              <div className="card-body">
                <h3 className="card-title">Sales & Enterprise Solutions</h3>
                <p>
                  Guidance on platform capabilities, pricing models, enterprise
                  deployment architecture, and custom integrations.
                </p>

                <div className="mt-4 text-sm opacity-80 space-y-1">
                  <p>• Product demos and onboarding</p>
                  <p>• Enterprise deployment planning</p>
                  <p>• Security compliance discussion</p>
                  <p>• Custom solution architecture</p>
                  <p>• Integration consulting</p>
                </div>
              </div>
            </div>

            <div className="card bg-white/90 backdrop-blur dark:bg-gray-800/90 shadow-lg">
              <div className="card-body">
                <h3 className="card-title">Technical Support</h3>
                <p>
                  Assistance with authentication, integrations, connectivity,
                  platform usage, and troubleshooting.
                </p>

                <div className="mt-4 text-sm opacity-80 space-y-1">
                  <p>• Account and login issues</p>
                  <p>• API and integration troubleshooting</p>
                  <p>• Platform configuration help</p>
                  <p>• Security and protection setup</p>
                  <p>• System diagnostics</p>
                </div>
              </div>
            </div>

            <div className="card bg-white/90 backdrop-blur dark:bg-gray-800/90 shadow-lg">
              <div className="card-body">
                <h3 className="card-title">Partnership & Collaboration</h3>
                <p>
                  Opportunities for technology partnerships, integrations,
                  research collaboration, and ecosystem development.
                </p>

                <div className="mt-4 text-sm opacity-80 space-y-1">
                  <p>• Integration partnerships</p>
                  <p>• Strategic alliances</p>
                  <p>• Technology collaboration</p>
                  <p>• Research initiatives</p>
                  <p>• Enterprise ecosystem development</p>
                </div>
              </div>
            </div>

          </div>
        </div>

      </section>

      {/* ---------- CONTACT FORM ---------- */}
      <section className="py-20 px-10 bg-white dark:bg-gray-800">
        <div className="max-w-4xl mx-auto">

          <h2 className="text-3xl font-bold text-center mb-4">
            Send Us a Message
          </h2>

          <p className="text-center opacity-80 mb-10">
            Provide details about your request and our team will respond with
            personalized guidance.
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">

            <div className="grid md:grid-cols-2 gap-6">
              <input
                name="name"
                value={formData.name}
                onChange={handleChange}
                type="text"
                placeholder="Full Name"
                className="input input-bordered w-full"
                required
              />

              <input
                name="email"
                value={formData.email}
                onChange={handleChange}
                type="email"
                placeholder="Email Address"
                className="input input-bordered w-full"
                required
              />
            </div>

            <input
              name="company"
              value={formData.company}
              onChange={handleChange}
              type="text"
              placeholder="Company / Organization (Optional)"
              className="input input-bordered w-full"
            />

            <select
              name="type"
              value={formData.type}
              onChange={handleChange}
              className="select select-bordered w-full"
            >
              <option value="general">General Inquiry</option>
              <option value="sales">Sales & Enterprise</option>
              <option value="support">Technical Support</option>
              <option value="partnership">Partnership</option>
            </select>

            <textarea
              name="message"
              value={formData.message}
              onChange={handleChange}
              className="textarea textarea-bordered w-full"
              rows={6}
              placeholder="Describe your request in detail..."
              required
            />

            <button className="btn btn-primary w-full">
              Send Message
            </button>

          </form>
        </div>
      </section>

      {/* ---------- RESPONSE & SUPPORT POLICY ---------- */}
      <section className="py-20 px-10">
        <div className="max-w-6xl mx-auto">

          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">
            Support & Response Policy
          </h2>

          <div className="grid md:grid-cols-3 gap-8 text-center">

            <div className="card bg-white dark:bg-gray-800 shadow-md">
              <div className="card-body">
                <h3 className="font-bold text-lg">Response Time</h3>
                <p className="text-3xl font-bold text-primary">{"< 24 Hours"}</p>
                <p className="opacity-80">Business day response for all inquiries</p>
              </div>
            </div>

            <div className="card bg-white dark:bg-gray-800 shadow-md">
              <div className="card-body">
                <h3 className="font-bold text-lg">Availability</h3>
                <p className="text-3xl font-bold text-primary">24/7</p>
                <p className="opacity-80">Monitoring and platform protection</p>
              </div>
            </div>

            <div className="card bg-white dark:bg-gray-800 shadow-md">
              <div className="card-body">
                <h3 className="font-bold text-lg">Global Support</h3>
                <p className="text-3xl font-bold text-primary">Worldwide</p>
                <p className="opacity-80">Enterprise and business customers</p>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* ---------- COMPANY INFO ---------- */}
      <section className="py-20 px-10 bg-white dark:bg-gray-800">
        <div className="max-w-5xl mx-auto text-center">

          <h2 className="text-3xl font-bold mb-8">
            Company Information
          </h2>

          <div className="stats shadow">

            <div className="stat">
              <div className="stat-title">Support Email</div>
              <div className="stat-value text-lg">support@securiva.ai</div>
              <div className="stat-desc">Primary support channel</div>
            </div>

            <div className="stat">
              <div className="stat-title">Headquarters</div>
              <div className="stat-value text-lg">Canada</div>
              <div className="stat-desc">Global infrastructure</div>
            </div>

            <div className="stat">
              <div className="stat-title">Security Commitment</div>
              <div className="stat-value text-lg">Enterprise Grade</div>
              <div className="stat-desc">Privacy and protection focused</div>
            </div>

          </div>
        </div>
      </section>

      {/* ---------- FAQ ---------- */}
      <section className="py-20 px-10">
        <div className="max-w-4xl mx-auto">

          <h2 className="text-3xl font-bold text-center mb-10">
            Frequently Asked Questions
          </h2>

          <div className="space-y-4">

            <div className="collapse collapse-arrow border bg-base-100">
              <input type="checkbox" />
              <div className="collapse-title font-medium">
                How quickly will I receive a response?
              </div>
              <div className="collapse-content">
                Most inquiries receive a response within 24 hours on business
                days. Enterprise customers may receive priority support.
              </div>
            </div>

            <div className="collapse collapse-arrow border bg-base-100">
              <input type="checkbox" />
              <div className="collapse-title font-medium">
                What information should I include in my message?
              </div>
              <div className="collapse-content">
                Include details about your use case, platform issue, or business
                requirements so our team can provide faster assistance.
              </div>
            </div>

            <div className="collapse collapse-arrow border bg-base-100">
              <input type="checkbox" />
              <div className="collapse-title font-medium">
                Do you provide enterprise deployment support?
              </div>
              <div className="collapse-content">
                Yes. We assist with architecture planning, integration design,
                and enterprise-scale deployments.
              </div>
            </div>

          </div>
        </div>
      </section>

    </div>
  );
}
