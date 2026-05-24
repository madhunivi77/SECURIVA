import ArticleTemplate from "../../components/ArticleTemplate";

export default function ShowcasePost() {
    return (
        <div>
            <ArticleTemplate title={"Capstone Showcase Press Release"} author={"ASU Capstone Team"} date={"May 1, 2026"} topic={"Presentation"} body={
                <div className="flex flex-col gap-3 pb-5">
                    <h2 className="font-bold">A Year in Development</h2>
                    <p>
                        After a full academic year of development, SecuriVA has evolved from a simple concept into a fully managed cybersecurity and AI platform designed to help businesses operate more securely and efficiently. What began as an ambitious capstone idea became a comprehensive solution that combines security infrastructure with intelligent workflow automation.
                    </p>

                    <p>
                        On Thursday, April 23, 2026, the SecuriVA team presented the platform at the Arizona State University capstone showcase event. The presentation highlighted several of the platform’s core features, including the AI voice agent, chatbot interface, on-premises packet monitoring system, and compliance management tools.
                    </p>

                    <p>
                        Throughout the showcase, students and attendees had the opportunity to interact directly with the platform through live demonstrations. One of the most engaging aspects of the event was the AI voice agent, which drew significant interest for its versatility and practical business applications. Attendees explored the different tools integrated into the AI system and saw firsthand how automation and security can work together within a single platform.
                    </p>

                    <p>
                        The feedback from the event was overwhelmingly positive. Many students were particularly interested in the breadth of functionality offered by SecuriVA, especially the combination of cybersecurity tooling with AI-driven assistance. The showcase served not only as an opportunity to demonstrate the team’s technical progress, but also as validation that the platform addresses real operational and security challenges faced by modern businesses.
                    </p>

                    <p>
                        As development continues beyond the academic year, the SecuriVA team remains focused on refining the platform, expanding its capabilities, and continuing to build solutions that make enterprise security and AI integration more accessible and effective.
                    </p>
                </div>
            } />
        </div>
    )
}