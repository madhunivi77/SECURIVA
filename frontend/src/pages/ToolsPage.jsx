import { Link } from "react-router-dom"

export default function ToolsPage() {
    function ToolCard({ cardTitle, cardSubtext, link, imgSrc }) {
        return (
            <Link to={link}>
                <div className="card w-90 shadow-sm transform transition duration-300 hover:scale-105 cursor-pointer"
                                style={{ background: "var(--bg-elev)", border: "1px solid var(--ivory-3)" }}
                    onMouseEnter={(e) => (e.currentTarget.style.borderColor = "var(--securiva-red)")}
                    onMouseLeave={(e) => (e.currentTarget.style.borderColor = "var(--ivory-3)")}
                >
                    <figure>
                        <img
                            src={imgSrc}
                            alt={cardTitle} />
                    </figure>
                    <div className="card-body text-black font-normal">
                        <h2 className="card-title" style={{ color: "var(--ink)" }} >{cardTitle}</h2>
                        <p style={{ color: "var(--ink-soft)" }} >{cardSubtext}</p>
                        <div className="card-actions justify-end">
                        </div>
                    </div>
                </div>
            </Link>
        )
    }

    return (
        <div className="h-full w-full">
            <div className="flex flex-wrap overflow-y-scroll h-[85vh] p-10 gap-5 items-start">

            <ToolCard 
                cardTitle="Firewall" 
                cardSubtext="View alerts from on premesis packet analysis and reporting" 
                imgSrc="/firewall.png"
                link="/dashboard/firewall"
            />

            </div>
        </div>
    )
}