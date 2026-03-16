// About.jsx
import Sponsors from "../components/Sponsors";

export default function About() {
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">

      {/* ---------- HERO ---------- */}
      <section className="hero py-24 bg-linear-to-br from-blue-900 to-black text-white">
        <div className="hero-content text-center max-w-4xl">
          <div>
            <h1 className="text-5xl font-bold mb-6">About SecuriVA</h1>
            <p className="text-xl opacity-90">
              SecuriVA is an enterprise AI platform that combines automation,
              cybersecurity, and secure communication into one unified system.
              We help organizations operate faster, safer, and smarter through
              intelligent technology built for the modern digital world.
            </p>
          </div>
        </div>
      </section>

      {/* ---------- COMPANY STORY ---------- */}
      <section className="py-20 px-10 max-w-6xl mx-auto">
        <div className="grid md:grid-cols-2 gap-12 items-center">

          <div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
              Our Story
            </h2>

            <p className="text-gray-700 dark:text-gray-300 mb-4">
              Modern businesses rely on dozens of disconnected tools to manage
              security, automation, and communication. This fragmentation
              creates complexity, increases risk, and slows innovation.
            </p>

            <p className="text-gray-700 dark:text-gray-300 mb-4">
              SecuriVA was built to solve this problem. We created a unified
              platform that integrates AI-driven automation, enterprise-grade
              cybersecurity protection, and secure communication infrastructure
              into one intelligent ecosystem.
            </p>

            <p className="text-gray-700 dark:text-gray-300">
              Our goal is simple: provide organizations with a digital system
              that works continuously in the background — protecting data,
              automating operations, and enhancing productivity.
            </p>
          </div>

          <div className="card shadow-xl bg-white dark:bg-gray-800">
            <div className="card-body">
              <h3 className="card-title">Built for Modern Enterprises</h3>
              <ul className="space-y-3 text-gray-600 dark:text-gray-300">
                <li>• AI-powered virtual assistance</li>
                <li>• Real-time threat detection</li>
                <li>• Secure AI networking and VPN</li>
                <li>• Automated communication management</li>
                <li>• Seamless integrations with business tools</li>
              </ul>
            </div>
          </div>

        </div>
      </section>

      {/* ---------- MISSION / VISION / VALUES ---------- */}
      <section className="py-20 px-10 bg-white dark:bg-gray-800">
        <div className="max-w-6xl mx-auto">

          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">
            Our Principles
          </h2>

          <div className="grid md:grid-cols-3 gap-8">

            <div className="card shadow-lg">
              <div className="card-body">
                <h3 className="card-title">Our Mission</h3>
                <p>
                  Empower organizations with secure AI systems that automate
                  operations, protect digital assets, and enhance human
                  productivity.
                </p>
              </div>
            </div>

            <div className="card shadow-lg">
              <div className="card-body">
                <h3 className="card-title">Our Vision</h3>
                <p>
                  A world where intelligent automation and cybersecurity work
                  together seamlessly to enable safe and efficient digital
                  transformation for every organization.
                </p>
              </div>
            </div>

            <div className="card shadow-lg">
              <div className="card-body">
                <h3 className="card-title">Our Values</h3>
                <ul className="space-y-2">
                  <li>• Security first</li>
                  <li>• Responsible AI innovation</li>
                  <li>• Privacy by design</li>
                  <li>• Reliability and trust</li>
                  <li>• Continuous improvement</li>
                </ul>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* ---------- PLATFORM OVERVIEW ---------- */}
      <section className="py-20 px-10">
        <div className="max-w-6xl mx-auto">

          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">
            The SecuriVA Platform
          </h2>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">

            <div className="card bg-white dark:bg-gray-800 shadow-md">
              <div className="card-body">
                <h3 className="card-title">AI Virtual Agent</h3>
                <p>
                  Automates workflows, communication, scheduling, and customer
                  interactions using intelligent conversational AI.
                </p>
              </div>
            </div>

            <div className="card bg-white dark:bg-gray-800 shadow-md">
              <div className="card-body">
                <h3 className="card-title">Cybersecurity Protection</h3>
                <p>
                  AI-driven defense systems monitor activity, detect threats,
                  and secure enterprise environments in real time.
                </p>
              </div>
            </div>

            <div className="card bg-white dark:bg-gray-800 shadow-md">
              <div className="card-body">
                <h3 className="card-title">Secure AI Networking</h3>
                <p>
                  Adaptive VPN and encrypted communication ensure safe
                  connections across distributed teams and systems.
                </p>
              </div>
            </div>

            <div className="card bg-white dark:bg-gray-800 shadow-md">
              <div className="card-body">
                <h3 className="card-title">Customer Interaction AI</h3>
                <p>
                  Manage calls, chats, and emails through an intelligent digital
                  assistant available 24/7.
                </p>
              </div>
            </div>

            <div className="card bg-white dark:bg-gray-800 shadow-md">
              <div className="card-body">
                <h3 className="card-title">eBook & Training Generator</h3>
                <p>
                  Create security awareness guides, documentation, and training
                  materials instantly using AI.
                </p>
              </div>
            </div>

            <div className="card bg-white dark:bg-gray-800 shadow-md">
              <div className="card-body">
                <h3 className="card-title">Enterprise Integrations</h3>
                <p>
                  Connect seamlessly with Gmail, Microsoft 365, Salesforce, and
                  other enterprise tools.
                </p>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* ---------- HOW IT WORKS ---------- */}
      <section className="py-20 px-10 bg-white dark:bg-gray-800">
        <div className="max-w-5xl mx-auto text-center">

          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-10">
            How SecuriVA Works
          </h2>

          <div className="steps steps-vertical md:steps-horizontal w-full">

            <div className="step step-primary">
              Connect your business systems and tools
            </div>

            <div className="step step-primary">
              AI analyzes workflows and security posture
            </div>

            <div className="step step-primary">
              Automation and protection activate instantly
            </div>

            <div className="step step-primary">
              Continuous monitoring and optimization
            </div>

          </div>

        </div>
      </section>
      <Sponsors className="bg-white pt-5 text-center text-black text-3xl"/>
    </div>
  );
}
