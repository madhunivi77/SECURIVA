import { Zap, Clock, MoreVertical, Play, Pause } from "lucide-react";
import { useTranslation } from "react-i18next";

const AutomationCard = ({
  title,
  description,
  isActive,
  lastRun,
  triggerCount,
  index
}) => {
  const { t } = useTranslation();

  return (
    <div className="p-5 border rounded-2xl border-gray-300 cursor-pointer">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-blue-200">
            <Zap className="h-5 w-5 text-blue-500" />
          </div>
          <div>
            <h3 className="font-medium">{title}</h3>
            <p className="text-sm">{description}</p>
          </div>
        </div>

        {/* More options */}
        <button className="flex justify-center items-center h-8 w-8 hover:bg-blue-200">
          <MoreVertical className="h-4 w-4 shrink-0" />
        </button>
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-gray-300">
        <div className="flex items-center gap-4">

          {/* Activity Badge */}
          <div className={isActive ? "badge badge-primary" : "badge badge-warning"}>
            {isActive
              ? t("automationCard.status.active")
              : t("automationCard.status.paused")}
          </div>

          {/* Last run tag */}
          <div className="flex items-center gap-1 text-sm">
            <Clock className="h-3.5 w-3.5" />
            {lastRun || t("automationCard.lastRun.neverRun")}
          </div>

        </div>

        <div className="flex items-center gap-2">

          {/* # of Runs */}
          <span className="text-sm">
            {triggerCount} {t("automationCard.runs.label")}
          </span>

          {/* Pause Button */}
          <button className="flex items-center justify-center h-8 w-8 text-gray-500 hover:text-black hover:bg-blue-200">
            {isActive
              ? <Pause className="h-4 w-4 shrink-0" />
              : <Play className="h-4 w-4 shrink-0" />}
          </button>

        </div>
      </div>
    </div>
  );
};

export default AutomationCard;