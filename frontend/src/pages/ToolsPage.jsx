import { Link, useOutletContext } from "react-router-dom";

export default function ToolsPage() {
    const { setHeading, setSubtext } = useOutletContext();
    setHeading("Cybersecurity Track");
    setSubtext("Your command center for cybersecurity tools and analytics");

    function ToolCard({ cardTitle, cardSubtext, link, imgSrc }) {
        return (
            <Link to={link}>
                <div className="card bg-white w-90 shadow-sm transform transition duration-300 hover:scale-105 cursor-pointer">
                    <figure>
                        <img
                            src={imgSrc}
                            alt={cardTitle} />
                    </figure>
                    <div className="card-body text-black font-normal">
                        <h2 className="card-title">{cardTitle}</h2>
                        <p>{cardSubtext}</p>
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