// About.jsx
import Sponsors from "../components/Sponsors";
import Card from "../components/Card";

export default function About() {
  return (
    <div className="min-h-screen bg-[#0a0f1f]">

      {/* ---------- HERO ---------- */}
      <section className="hero py-24 text-white">
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
      <section className="relative pt-20 mx-auto overflow-hidden">

        <div className="relative w-full min-h-screen overflow-hidden bg-black mx-auto">
          <video
            autoPlay
            loop
            muted
            playsInline
            className="absolute top-0 left-0 w-full h-full object-cover opacity-50"
          >
            <source src="/landing_page/banner.mp4" type="video/mp4" />
            Your browser does not support the video tag.
          </video>

          <div className="absolute top-0 left-0 w-full h-64 bg-gradient-to-b from-[#0a0f1f] via-[#0a0f1f]/60 to-transparent pointer-events-none"></div>

          <div className="absolute bottom-0 left-0 w-full h-64 bg-gradient-to-t from-black via-black/60 to-transparent pointer-events-none"></div>

          <div className="relative z-5 flex flex-col md:flex-row items-center justify-center gap-8 px-6 py-20">
            <div className="card shadow-xl bg-white/90 backdrop-blur dark:bg-gray-800/90 max-h-200 max-w-200">
              <div className="card-body  text-xl">
                <h3 className="card-title text-3xl font-bold text-gray-900 dark:text-white mb-6">
                  Our Story
                </h3>

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
            </div>

            <div className="card shadow-xl bg-white/90 backdrop-blur dark:bg-gray-800/90 min-h-110 max-h-200 max-w-200">
              <div className="card-body">
                <h3 className="card-title">Built for Modern Enterprises</h3>
                <ul className="space-y-3 text-gray-600 dark:text-gray-300 text-xl">
                  <li>• AI-powered virtual assistance</li>
                  <li>• Real-time threat detection</li>
                  <li>• Secure AI networking and VPN</li>
                  <li>• Automated communication management</li>
                  <li>• Seamless integrations with business tools</li>
                </ul>
              </div>
            </div>
          </div>

        </div>

      </section>

      {/* ---------- MISSION / VISION / VALUES ---------- */}
      <section className="bg-black">
        <div className="max-w-6xl mx-auto">

          <h2 className="text-5xl font-bold text-center text-gray-900 dark:text-white mb-12">
            Our Principles
          </h2>

          <div className="grid md:grid-cols-3 gap-8">

            <div className="card shadow-lg">
              <div className="card-body text-xl">
                <h3 className="card-title text-xl">Our Mission</h3>
                <p>
                  Empower organizations with secure AI systems that automate
                  operations, protect digital assets, and enhance human
                  productivity.
                </p>
              </div>
            </div>

            <div className="card shadow-lg">
              <div className="card-body text-xl">
                <h3 className="card-title text-xl">Our Vision</h3>
                <p>
                  A world where intelligent automation and cybersecurity work
                  together seamlessly to enable safe and efficient digital
                  transformation for every organization.
                </p>
              </div>
            </div>

            <div className="card shadow-lg">
              <div className="card-body text-xl">
                <h3 className="card-title text-xl">Our Values</h3>
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
      <section className="bg-black">
        <div className="mx-auto text-black">

          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">
            The SecuriVA Platform
          </h2>

          <div
            id="feature-cards"
            className="flex flex-wrap justify-center gap-12.5 pb-20 pt-9 mx-0"
          >

            <Card
              className={"w-auto sm:w-[25%]"}
              image={"landing_page/AI_Virtual_assistant.png"}
              title={"AI Virtual Agent"}
              text={
                "Automates workflows, communication, scheduling, and customer interactions using intelligent conversational AI."
              }
            />

            <Card
              className={"w-auto sm:w-[25%]"}
              image={"landing_page/Cybersecurity_Protection.png"}
              title={"Cybersecurity Protection"}
              text={
                "AI-driven defense systems monitor activity, detect threats, and secure enterprise environments in real time."
              }
            />

            <Card
              className={"w-auto sm:w-[25%]"}
              image={"landing_page/AI_VPN.png"}
              title={"Secure AI Networking"}
              text={
                "Adaptive VPN and encrypted communication ensure safe connections across distributed teams and systems."
              }
            />

            <Card
              className={"w-auto sm:w-[25%]"}
              image={"landing_page/Customer_Interaction.png"}
              title={"Customer Interaction AI"}
              text={
                "Manage calls, chats, and emails through an intelligent digital assistant available 24/7."
              }
            />

            <Card
              className={"w-auto sm:w-[25%]"}
              image={"landing_page/ebook.png"}
              title={"eBook & Training Generator"}
              text={
                "Create security awareness guides, documentation, and training materials instantly using AI."
              }
            />

            <Card
              className={"w-auto sm:w-[25%]"}
              image={"landing_page/Integrations.png"}
              title={"Enterprise Integrations"}
              text={
                "Connect seamlessly with Gmail, Microsoft 365, Salesforce, and other enterprise tools."
              }
            />

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
      <Sponsors className="bg-white pt-5 text-center text-black text-3xl" />
    </div>
  );
}
