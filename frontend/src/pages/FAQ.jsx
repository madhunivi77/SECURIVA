export default function FAQ() {
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
        {/* ---------- FAQ ---------- */}
        <section className="px-20 pb-20">
            <h2 className="text-4xl font-mono text-center mb-12 pt-10">
                Frequently Asked Questions
            </h2>

            <div className="max-w-4xl mx-auto space-y-4">

                <div className="collapse collapse-arrow bg-[#111633]">
                <input type="checkbox" defaultChecked />
                <div className="collapse-title text-lg font-medium">
                    What is SecuriVA?
                </div>
                <div className="collapse-content text-blue-200">
                    SecuriVA is an AI-powered virtual assistant platform designed to automate business processes, enhance customer interactions, and provide enterprise-grade cybersecurity. It integrates with tools such as email, CRM systems, WhatsApp, payment APIs, and productivity suites.
                </div>
                </div>

                <div className="collapse collapse-arrow bg-[#111633]">
                <input type="checkbox" defaultChecked/>
                <div className="collapse-title text-lg font-medium">
                    What can SecuriVA do for my business?
                </div>
                <div className="collapse-content text-blue-200">
                    SecuriVA can automate administrative tasks, manage communication (email, calls, video), process workflows, detect cyber threats, secure sensitive data, and integrate seamlessly with your existing tools.
                </div>
                </div>

                <div className="collapse collapse-arrow bg-[#111633]">
                <input type="checkbox" defaultChecked/>
                <div className="collapse-title text-lg font-medium">
                    Who is SecuriVA designed for?
                </div>
                <div className="collapse-content text-blue-200">
                    SecuriVA is designed for small businesses, enterprises, e-commerce platforms, fintech companies, healthcare organizations, educational institutions, and professionals seeking automation and secure AI workflows.
                </div>
                </div>

                <div className="collapse collapse-arrow bg-[#111633]">
                <input type="checkbox" defaultChecked/>
                <div className="collapse-title text-lg font-medium">
                    Does SecuriVA support multiple languages?
                </div>
                <div className="collapse-content text-blue-200">
                    Yes. SecuriVA operates in multilingual environments and supports AI-based translation layers.
                </div>
                </div>

                <div className="collapse collapse-arrow bg-[#111633]">
                <input type="checkbox" defaultChecked/>
                <div className="collapse-title text-lg font-medium">
                    Is SecuriVA cloud-based or on-premise?
                </div>
                <div className="collapse-content text-blue-200">
                    SecuriVA is cloud-based with optional enterprise on-premise or hybrid deployments available.
                </div>
                </div>

                <div className="collapse collapse-arrow bg-[#111633]">
                <input type="checkbox" defaultChecked/>
                <div className="collapse-title text-lg font-medium">
                    How secure is SecuriVA?
                </div>
                <div className="collapse-content text-blue-200">
                    SecuriVA follows enterprise-grade security standards, including encryption, role-based access control, continuous monitoring, and compliance with GDPR, HIPAA, and PCI-DSS.
                </div>
                </div>

            </div>
        </section>
    </div>
  );
}

