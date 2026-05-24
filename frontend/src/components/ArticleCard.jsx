import { Link } from "react-router-dom";

export default function ArticleCard({ title, date, image, link }) {
    return (
        <div className="group">
            <Link to={link}>
                <div className="w-75">
                    <figure>
                        <img
                            src={image}
                            alt={title} />
                    </figure>

                    {/* Title/Caption */}
                    <h2 className="group-hover:underline text-lg font-bold pt-1">
                        {title}
                    </h2>

                    <p className="text-sm">{date}</p>
                </div>
            </Link>
        </div>
    )
}