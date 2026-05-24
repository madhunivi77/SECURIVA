import { useTranslation } from "react-i18next";
import { User } from "lucide-react";

export default function ArticleTemplate({ title, author, date, topic, body }) {
    const { t } = useTranslation();
    return (
        <div className="mx-5 lg:mx-[15%] pt-5">
            <h1 className="text-center lg:text-left">{title}</h1>
            <div className="flex flex-col lg:flex-row gap-2 py-5">
                <div className="badge">{topic}</div>
                <div className="flex flex-row gap-2 items-center">
                    <User className="text-white w-4 h-4"/>
                    <p><span className="font-extrabold">{author}</span> on {date}</p>
                </div>
            </div>
            <div>{body}</div>
        </div>
    )
}