import { useTranslation } from "react-i18next";
import ArticleCard from "../components/ArticleCard";
import FeaturedArticle from "../components/FeaturedArticle";

export default function Blog() {
    const { t } = useTranslation();
    return (
        <div className="section-min-height">
            <header className="bg-[url('/blog_banner.png')] bg-cover bg-center h-64 flex items-center justify-center">
                <h1 className="text-[30px] text-center px-5">The SecuriVA Blog</h1>
            </header>
            {/* Body */}
            <div className="flex flex-col-reverse lg:flex-row gap-10 p-5 lg:px-20 lg:pt-10 items-center lg:items-start">
                {/* Articles Section*/}
                <div className="flex-3">
                    <p className="text-2xl font-bold pb-5 text-center lg:text-left">Articles</p>
                    <div className="flex flex-wrap justify-center lg:justify-start gap-3">
                        <ArticleCard image={"/first_post.png"} title={"Introduction to SecuriVA"} date={"May 1, 2026"} link={"/blog/showcase"} />
                    </div>
                </div>
                {/* Sidebar with featured articles and newsletter*/}
                <div className="flex-1">
                    <div className="flex flex-col gap-5">
                        <p className="text-2xl font-bold pb-5 text-center lg:text-left">Featured Articles</p>
                        <FeaturedArticle image={"/first_post.png"} title={"Capstone Showcase Press Release"} date={"May 1, 2026"} link={"/blog/showcase"} />
                    </div>
                </div>
            </div>
        </div>
    )
}