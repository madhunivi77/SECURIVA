import { useTranslation } from "react-i18next";

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div className="flex gap-2">
      <button
        onClick={() => changeLanguage("en")}
        className="px-3 py-1 rounded bg-red-300 hover:bg-red-400 text-black"
      >
        EN
      </button>

      <button
        onClick={() => changeLanguage("fr")}
        className="px-3 py-1 rounded bg-red-300 hover:bg-red-400 text-black"
      >
        FR
      </button>
    </div>
  );
}