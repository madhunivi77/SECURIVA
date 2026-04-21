import { MessageSquarePlus, Mic, Settings, User, Workflow } from "lucide-react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

const Sidebar = () => {
  const { t } = useTranslation();

  return (
    <aside className="flex flex-col h-full w-64 border-r border-gray-300">

      {/* Logo area */}
      <div className="p-4 border-b border-border border-gray-300">
        <img src="logo.png" alt="Logo" />
      </div>

      {/* New Chat Button */}
      <Link to="/dashboard/chat" className="m-2">
        <button className="inline-flex justify-normal w-full items-center text-black bg-gray-200 border-gray-300 gap-4">
          <MessageSquarePlus className="w-4 h-4" />
          {t("sidebar.buttons.newChat")}
        </button>
      </Link>

      {/* Voice Agent Button */}
      <Link to="/dashboard/voice" className="m-2">
        <button className="inline-flex justify-normal w-full items-center text-black bg-gray-200 border-gray-300 gap-4">
          <Mic className="w-4 h-4" />
          {t("sidebar.buttons.voiceAgent")}
        </button>
      </Link>

      {/* Automations Button */}
      <Link to="/dashboard" className="m-2">
        <button className="inline-flex justify-normal w-full items-center text-black bg-gray-200 border-gray-300 gap-4">
          <Workflow className="w-4 h-4" />
          {t("sidebar.buttons.automations")}
        </button>
      </Link>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Bottom buttons */}
      <div className="p-4 space-y-2 border-t border-border border-gray-300">

        <button className="inline-flex items-center justify-normal gap-4 m-2">
          <Settings className="w-4 h-4" />
          {t("sidebar.buttons.settings")}
        </button>

        <button className="inline-flex items-center justify-normal gap-4 m-2">
          <User className="w-4 h-4" />
          {t("sidebar.buttons.account")}
        </button>

      </div>

    </aside>
  );
};

export default Sidebar;