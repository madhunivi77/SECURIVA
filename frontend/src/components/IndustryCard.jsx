import { AlertTriangle, Lightbulb, TrendingUp, CheckCircle2 } from "lucide-react";
import { useTranslation } from "react-i18next";

const IndustryCard = ({ challenges, solutions, impact, className }) => {
  const { t } = useTranslation();

  return (
    <div className={`rounded-2xl border p-6 border-gray-800 bg-inherit ${className}`}>

      <div className="flex flex-wrap gap-6">

        {/* Challenges */}
        <div className="flex-1 min-w-40">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="h-4 w-4 stroke-amber-500" strokeWidth={1.5} />
            <p className="text-xl font-medium uppercase tracking-widest text-gray-600">
              {t("industryCard.challenges")}
            </p>
          </div>

          <ul className="flex flex-col gap-1.5">
            {challenges.map((item) => (
              <li key={item} className="flex items-start gap-2 text-lg text-gray-300">
                <CheckCircle2 className="mt-2 h-3.5 w-3.5 shrink-0 stroke-amber-500" strokeWidth={2} />
                {item}
              </li>
            ))}
          </ul>
        </div>

        {/* Solutions */}
        <div className="flex-1 min-w-40">
          <div className="flex items-center gap-2 mb-3">
            <Lightbulb className="h-4 w-4 stroke-blue-500" strokeWidth={1.5} />
            <p className="text-xl font-medium uppercase tracking-widest text-gray-600">
              {t("industryCard.solutions")}
            </p>
          </div>

          <ul className="flex flex-col gap-1.5">
            {solutions.map((item) => (
              <li key={item} className="flex items-start gap-2 text-lg text-gray-300">
                <CheckCircle2 className="mt-2 h-3.5 w-3.5 shrink-0 stroke-blue-500" strokeWidth={2} />
                {item}
              </li>
            ))}
          </ul>
        </div>

        {/* Impact */}
        <div className="flex-1 min-w-40">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="h-4 w-4 stroke-green-500" strokeWidth={1.5} />
            <p className="text-xl font-medium uppercase tracking-widest text-gray-600">
              {t("industryCard.impact")}
            </p>
          </div>

          <ul className="flex flex-col gap-1.5">
            {impact.map((item) => (
              <li key={item} className="flex items-start gap-2 text-lg text-gray-300">
                <CheckCircle2 className="mt-2 h-3.5 w-3.5 shrink-0 stroke-green-500" strokeWidth={2} />
                {item}
              </li>
            ))}
          </ul>
        </div>

      </div>
    </div>
  );
};

export default IndustryCard;