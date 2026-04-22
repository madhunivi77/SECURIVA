import { Check } from "lucide-react";
import { useTranslation } from "react-i18next";

function Feature({ children }) {
  return (
    <div className="flex gap-3 items-start">
      <Check size={18} className="mt-1 shrink-0 text-primary" />
      <span>{children}</span>
    </div>
  );
}

export default function Pricing() {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen flex flex-col gap-8 items-center py-24 px-4">

      {/* Title */}
      <div className="flex flex-col gap-2 text-center">
        <h1 className="font-bold text-3xl">{t("pricing.title")}</h1>
        <span className="text-base-content/70">
          {t("pricing.subtitle")}
        </span>
      </div>

      {/* Pricing cards */}
      <div className="flex flex-col md:flex-row gap-8 px-2 max-w-6xl w-full items-center md:items-stretch justify-center">

        {/* Starter */}
        <div className="flex flex-col gap-6 bg-[#091932] rounded-box p-8 flex-1 max-w-sm">

          <div className="flex flex-col gap-4 text-center pt-13">
            <h2 className="text-xl">{t("pricing.starter.name")}</h2>

            <h1 className="text-5xl font-bold">
              {t("pricing.starter.price")}
            </h1>

            <span className="text-sm">
              {t("pricing.starter.description")}
            </span>
          </div>

          <div className="flex flex-col gap-2 flex-1">
            {t("pricing.starter.features", { returnObjects: true }).map((f, i) => (
              <Feature key={i}>{f}</Feature>
            ))}
          </div>

          <button className="btn btn-neutral">
            {t("pricing.starter.button")}
          </button>
        </div>

        {/* Professional */}
        <div className="flex flex-col gap-6 bg-[#091932] rounded-box p-8 border border-primary shadow flex-1 max-w-sm">

          <div className="badge badge-primary self-center badge-lg">
            {t("pricing.professional.badge")}
          </div>

          <div className="flex flex-col gap-4 text-center">
            <h2 className="text-xl">{t("pricing.professional.name")}</h2>

            <h1 className="text-5xl font-bold">
              {t("pricing.professional.price")}
            </h1>

            <span className="text-sm">
              {t("pricing.professional.description")}
            </span>
          </div>

          <div className="flex flex-col gap-2 flex-1">
            {t("pricing.professional.features", { returnObjects: true }).map((f, i) => (
              <Feature key={i}>{f}</Feature>
            ))}
          </div>

          <button className="btn btn-primary">
            {t("pricing.professional.button")}
          </button>
        </div>

        {/* Enterprise */}
        <div className="flex flex-col gap-6 bg-[#091932] rounded-box p-8 flex-1 max-w-sm">

          <div className="flex flex-col gap-4 text-center pt-13">
            <h2 className="text-xl">{t("pricing.enterprise.name")}</h2>

            <h1 className="text-5xl font-bold">
              {t("pricing.enterprise.price")}
            </h1>

            <span className="text-sm">
              {t("pricing.enterprise.description")}
            </span>
          </div>

          <div className="flex flex-col gap-2 flex-1">
            {t("pricing.enterprise.features", { returnObjects: true }).map((f, i) => (
              <Feature key={i}>{f}</Feature>
            ))}
          </div>

          <button className="btn btn-neutral">
            {t("pricing.enterprise.button")}
          </button>
        </div>

      </div>
    </div>
  );
}