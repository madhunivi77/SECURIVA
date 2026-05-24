import { useTranslation } from "react-i18next";
export default function ComingSoon() {
    const { t } = useTranslation();
    return (
        <div>
            <header className="hero section-min-height">
                <div className="hero-content flex justify-evenly">
                    <div>
                        <h1 className="text-[40px] text-center pt-5">{t("comingsoon.title")}</h1>
                        <p className="text-[25px] text-center pt-7.5 pb-10">
                            {t("comingsoon.subtext")}
                        </p>
                    </div>
                </div>
            </header>
        </div>
    )
}