import { useTranslation } from "react-i18next";

function Sponsors({ className}) {
  const { t } = useTranslation();
  // Combine internal classes with the passed className prop
  const combinedClasses = `${className || ''}`.trim();
  return (
    <div className={combinedClasses}>
        <h2>{t("sponsors.title")}</h2>
        <div className="flex flex-col lg:flex-row p-6 max-w-full justify-between items-center">
            <img src={"/LOGOS(46).png"} className="flex-1 h-auto object-contain max-h-25" />
            <img src={"/LOGOS(47).png"} className="flex-1 h-auto object-contain max-h-50" />
            <img src={"/LOGOS(48).png"} className="flex-1 h-auto object-contain max-h-50" />
            <img src={"/LOGOS(49).png"} className="flex-1 h-auto object-contain max-h-50" />
        </div>
    </div>
);
}

export default Sponsors;