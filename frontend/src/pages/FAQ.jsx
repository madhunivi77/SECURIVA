import { useState } from "react";
import faqData from "../data/faqData.json";
import { Search } from "lucide-react";

export default function FAQ() {
    const [query, setQuery] = useState("");

    const filtered = faqData
    .map(section => ({
      ...section,
      items: section.items.filter(item =>
        item.question.toLowerCase().includes(query.toLowerCase()) || item.answer.toLowerCase().includes(query.toLowerCase())
      ),
    }))
    .filter(section => section.items.length > 0);

    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
            {/* ---------- FAQ ---------- */}
            <section className="px-20 pb-20">
                <h2 className="text-4xl font-mono text-center mb-5 pt-10">
                    Frequently Asked Questions
                </h2>
                {/* Search bar */}
                <div className="flex gap-2 border border-b-white rounded-2xl mx-auto w-125 p-2 mb-12">
                    <Search/>
                    <input type="text" id="search-input" placeholder="Search" className="focus:outline-none focus:ring-0 flex-1" value={query}
                        onChange={(e) => setQuery(e.target.value)}/>
                </div>
                <div className="max-w-4xl mx-auto space-y-12">
                    {filtered.map((categoryBlock) => (
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

