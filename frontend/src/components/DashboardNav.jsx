import { LogOut, Plus, RotateCcw } from "lucide-react";
import { Link } from "react-router-dom";
import LanguageSwitcher from "./LanguageSwitcher";
import { useTranslation } from "react-i18next";

export default function DashboardNav({ onCreateAutomation, onRefresh }) {
  const { t } = useTranslation();

  return (
    <header className="flex items-center justify-between h-16 px-6 border-b border-border border-gray-300">
      <div>
        <h2 className="text-xl font-medium">
          {t("dashboardNav.title")}
        </h2>
        <p className="text-md">
          {t("dashboardNav.subtitle")}
        </p>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex justify-end p-4">
          <LanguageSwitcher />
        </div>

        {/* Refresh Button */}
        <button onClick={onRefresh} title={t("dashboardNav.tooltips.refresh")}>
          <RotateCcw className="h-4 w-4" />
        </button>

        {/* New Automation Button */}
        <button className="btn glass-button justify-normal gap-4 m-2">
          <Plus className="w-4 h-4" />
          {t("dashboardNav.buttons.newAutomation")}
        </button>

        {/* Logout Button */}
        <Link to="/" title={t("dashboardNav.tooltips.logout")}>
          <button className="hover:bg-red-300">
            <LogOut className="h-4 w-4" />
          </button>
        </Link>
      </div>
    </header>
  );
}