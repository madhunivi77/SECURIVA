import { Link } from "react-router-dom";

export default function FeaturedArticle({ title, date, image, link }) {
    return (
        <div className="group">
            <Link to={link}>
                <div className="flex gap-3">
                    <figure>
                        <img
                            src={image}
                            alt={title} 
                            className="aspect-square w-30 rounded-full object-cover"/>
                    </figure>

                    <div className="flex flex-col justify-center">
                    {/* Title/Caption */}
                    <h2 className="group-hover:underline text-lg font-bold">
                        {title}
                    </h2>

                    <p className="text-sm">{date}</p>
                    </div>
                </div>
            </Link>
        </div>
    )
}