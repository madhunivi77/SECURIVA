// Support.jsx
import { useState } from "react";

export default function Support() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    category: "Technical Issue",
    message: "",
  });

  const handleChange = (e) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    alert("Support request submitted. Our team will contact you shortly.");
    setFormData({
      name: "",
      email: "",
      category: "Technical Issue",
      message: "",
    });
  };

  return (
    <div className="bg-[#0a0f1f] text-white">

      {/* ---------- HERO ---------- */}
      <section className="pt-32 pb-24 px-20 text-center">
        <h1 className="text-5xl font-mono font-bold mb-6">
          SecuriVA Support Center
        </h1>
        <p className="text-2xl text-blue-200 max-w-4xl mx-auto">
          Professional assistance for platform usage, integrations,
          cybersecurity configuration, and enterprise operations.
          Our support team ensures reliability, security, and seamless
          automation across your workflows.
        </p>
      </section>

      {/* ---------- SUPPORT AREAS ---------- */}
      <section className="px-20 pb-20">
        <h2 className="text-4xl font-mono text-center mb-12">
          Support Areas
        </h2>

        <div className="grid md:grid-cols-3 gap-10">

          <div className="card bg-[#111633] shadow-xl">
            <div className="card-body">
              <h3 className="card-title text-xl">Account & Authentication</h3>
              <p className="text-blue-200">
                Assistance with login issues, Google authentication,
                account access permissions, session problems,
                and identity verification.
              </p>

              <div className="text-sm opacity-80 mt-3">
                <p className="font-semibold">Common issues we help with:</p>
                <ul className="list-disc ml-6 mt-2 space-y-1">
                  <li>Login failures or access restrictions</li>
                  <li>Account configuration or role permissions</li>
                  <li>Authentication errors</li>
                  <li>Session timeout or verification issues</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="card bg-[#111633] shadow-xl">
            <div className="card-body">
              <h3 className="card-title text-xl">Platform & Integrations</h3>
              <p className="text-blue-200">
                Support for Salesforce connections, API integrations,
                automation workflows, system configuration,
                and data synchronization issues.
              </p>

              <div className="text-sm opacity-80 mt-3">
                <p className="font-semibold">We assist with:</p>
                <ul className="list-disc ml-6 mt-2 space-y-1">
                  <li>Integration setup and troubleshooting</li>
                  <li>Workflow automation configuration</li>
                  <li>API connectivity issues</li>
                  <li>System performance optimization</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="card bg-[#111633] shadow-xl">
            <div className="card-body">
              <h3 className="card-title text-xl">Security & Privacy</h3>
              <p className="text-blue-200">
                Guidance on secure configuration, data protection,
                encryption practices, and cybersecurity best practices.
              </p>

              <div className="text-sm opacity-80 mt-3">
                <p className="font-semibold">Coverage includes:</p>
                <ul className="list-disc ml-6 mt-2 space-y-1">
                  <li>Security configuration recommendations</li>
                  <li>Data protection practices</li>
                  <li>Privacy and compliance questions</li>
                  <li>Incident response guidance</li>
                </ul>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* ---------- SUPPORT PROCESS ---------- */}
      <section className="px-20 pb-20">
        <div className="bg-[#000020]/90 rounded-2xl p-10">
          <h2 className="text-3xl font-mono text-center mb-8">
            How Our Support Process Works
          </h2>

          <div className="grid md:grid-cols-4 gap-8 text-center">

            <div>
              <div className="text-4xl font-bold text-blue-400 mb-2">1</div>
              <p className="font-semibold">Submit Request</p>
              <p className="text-sm text-blue-200 mt-2">
                Provide details about your issue, environment,
                and expected outcome.
              </p>
            </div>

            <div>
              <div className="text-4xl font-bold text-blue-400 mb-2">2</div>
              <p className="font-semibold">Issue Review</p>
              <p className="text-sm text-blue-200 mt-2">
                Our engineers analyze logs, configuration,
                and system behavior.
              </p>
            </div>

            <div>
              <div className="text-4xl font-bold text-blue-400 mb-2">3</div>
              <p className="font-semibold">Resolution</p>
              <p className="text-sm text-blue-200 mt-2">
                We provide fixes, recommendations,
                or guided troubleshooting.
              </p>
            </div>

            <div>
              <div className="text-4xl font-bold text-blue-400 mb-2">4</div>
              <p className="font-semibold">Follow-Up</p>
              <p className="text-sm text-blue-200 mt-2">
                Continued monitoring ensures stable operation.
              </p>
            </div>

          </div>
        </div>
      </section>

      {/* ---------- FAQ ---------- */}
      <section className="px-20 pb-20">
        <h2 className="text-4xl font-mono text-center mb-12">
          Frequently Asked Questions
        </h2>

        <div className="max-w-4xl mx-auto space-y-4">

          <div className="collapse collapse-arrow bg-[#111633]">
            <input type="checkbox" />
            <div className="collapse-title text-lg font-medium">
              How do I connect Salesforce to SecuriVA?
            </div>
            <div className="collapse-content text-blue-200">
              After logging in, navigate to your dashboard and choose
              the integration setup option. Follow the authorization
              steps to connect your Salesforce environment securely.
            </div>
          </div>

          <div className="collapse collapse-arrow bg-[#111633]">
            <input type="checkbox" />
            <div className="collapse-title text-lg font-medium">
              How quickly will I receive a response?
            </div>
            <div className="collapse-content text-blue-200">
              Standard support responses are provided within 24 hours.
              Enterprise support requests receive priority handling
              and faster response times.
            </div>
          </div>

          <div className="collapse collapse-arrow bg-[#111633]">
            <input type="checkbox" />
            <div className="collapse-title text-lg font-medium">
              What information should I include in my request?
            </div>
            <div className="collapse-content text-blue-200">
              Include your environment details, steps to reproduce the
              issue, error messages, and expected behavior. This helps
              our engineers resolve your issue faster.
            </div>
          </div>

          <div className="collapse collapse-arrow bg-[#111633]">
            <input type="checkbox" />
            <div className="collapse-title text-lg font-medium">
              Is my data secure when contacting support?
            </div>
            <div className="collapse-content text-blue-200">
              Yes. All support communications follow secure handling
              practices and confidentiality standards.
            </div>
          </div>

        </div>
      </section>

      {/* ---------- SUPPORT FORM ---------- */}
      <section className="px-20 pb-20">
        <div className="max-w-3xl mx-auto bg-[#111633] p-10 rounded-2xl shadow-xl">
          <h2 className="text-3xl font-mono mb-6 text-center">
            Submit a Support Request
          </h2>

          <form onSubmit={handleSubmit} className="space-y-6">

            <input
              type="text"
              name="name"
              placeholder="Full Name"
              className="input input-bordered w-full"
              value={formData.name}
              onChange={handleChange}
              required
            />

            <input
              type="email"
              name="email"
              placeholder="Business Email"
              className="input input-bordered w-full"
              value={formData.email}
              onChange={handleChange}
              required
            />

            <select
              name="category"
              className="select select-bordered w-full"
              value={formData.category}
              onChange={handleChange}
            >
              <option>Technical Issue</option>
              <option>Account Help</option>
              <option>Integration Support</option>
              <option>Security Question</option>
              <option>Partnership Inquiry</option>
              <option>Billing</option>
              <option>Other</option>
            </select>

            <textarea
              name="message"
              placeholder="Describe your issue or request..."
              className="textarea textarea-bordered w-full h-40"
              value={formData.message}
              onChange={handleChange}
              required
            />

            <button className="btn btn-primary w-full text-lg">
              Submit Request
            </button>

          </form>
        </div>
      </section>

      {/* ---------- SERVICE COMMITMENT ---------- */}
      <section className="px-20 pb-24 text-center">
        <h2 className="text-3xl font-mono mb-4">
          Enterprise Support Commitment
        </h2>

        <p className="text-blue-200 text-lg max-w-3xl mx-auto">
          SecuriVA provides enterprise-grade reliability with continuous
          monitoring, rapid issue response, and proactive system health
          management to ensure uninterrupted operations.
        </p>

        <div className="mt-8 flex justify-center gap-6 flex-wrap">
          <div className="badge badge-lg badge-outline">
            24/7 Platform Monitoring
          </div>
          <div className="badge badge-lg badge-outline">
            24hr Standard Response
          </div>
          <div className="badge badge-lg badge-outline">
            Priority Enterprise Support
          </div>
          <div className="badge badge-lg badge-outline">
            Secure Communication Channels
          </div>
        </div>
      </section>

    </div>
  );
}
