import faqData from "../data/faqData.json";

export default function FAQ() {
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
        {/* ---------- FAQ ---------- */}
        <section className="px-20 pb-20">
            <h2 className="text-4xl font-mono text-center mb-12 pt-10">
                Frequently Asked Questions
            </h2>

            <div className="max-w-4xl mx-auto space-y-12">
                {faqData.map((categoryBlock) => (
                <div key={categoryBlock.category}>
                    
                    {/* Category Subheading */}
                    <h3 className="text-2xl font-semibold mb-6 text-blue-300">
                    {categoryBlock.category}
                    </h3>

                    {/* Questions */}
                    <div className="space-y-4">
                    {categoryBlock.items.map((faq, index) => (
                        <div
                        key={faq.id}
                        className="collapse collapse-arrow bg-[#111633]"
                        >
                        <input type="checkbox" />
                        <div className="collapse-title text-lg font-medium">
                            {faq.question}
                        </div>
                        <div className="collapse-content text-blue-200">
                            {faq.answer}
                        </div>
                        </div>
                    ))}
                    </div>

                </div>
                ))}
            </div>
        </section>
    </div>
  );
}

