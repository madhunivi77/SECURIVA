import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ChevronLeft } from "lucide-react";
import Copyright from "../components/Copyright";
import { useTranslation } from "react-i18next";

export default function ProviderForm() {
  const { t } = useTranslation();

  const { isAuthenticated, loginGoogle, loginSalesforce } = useAuth();

  const [loadingGoogle, setLoadingGoogle] = useState(false);
  const [loadingSalesforce, setLoadingSalesforce] = useState(false);

  const navigate = useNavigate();

  const handleGoogleLogin = () => {
    setLoadingGoogle(true);
    loginGoogle();
  };

  const handleSalesforceLogin = () => {
    setLoadingSalesforce(true);
    loginSalesforce();
  };

  return (
    <div className="bg-[#000020] w-screen min-h-screen flex flex-col justify-between">
      <div>
        <button onClick={() => navigate(-1)} className="text-white absolute top-0 left-0">
          <ChevronLeft />
        </button>

        <div className="flex flex-col-reverse md:flex-row justify-center gap-10 text-center">

          {/* VIDEO */}
          <div className="flex flex-col justify-center w-auto md:w-[40%] pt-0 md:pt-20">
            <video autoPlay loop muted playsInline>
              <source src="/landing_page/SecurivaHero.mp4" type="video/mp4" />
            </video>
          </div>

          {/* FORM */}
          <div className="flex flex-col pr-0 md:pr-10 mx-auto md:mx-0 md:max-w-none w-auto md:w-[35%] justify-center pt-10 font-sans text-white">

            <img src="LOGO_FOOTER_0000.png" className="pb-5 w-50 mx-auto" />

            <h2 className="text-2xl font-semibold pb-3">
              {t("providerForm.title")}
            </h2>

            <input
              className="input validator bg-slate-800 border-black text-white mb-3 w-full"
              type="email"
              required
              placeholder={t("providerForm.emailPlaceholder")}
            />

            {/* Continue */}
            <button
              className="w-full px-3 py-5 mb-3 bg-[#4285F4] text-white border-none rounded-sm text-4 font-medium flex items-center justify-center gap-3 hover:bg-[#357ae8]"
              style={{
                cursor: loadingGoogle ? "default" : "pointer",
                opacity: loadingGoogle ? 0.7 : 1
              }}
            >
              {t("providerForm.continue")}
            </button>

            <h2 className="text-xl font-semibold pb-3 whitespace-pre-line">
              {t("providerForm.otherLogin")}
            </h2>

            {/* GOOGLE */}
            <button
              className="w-full px-3 py-5 mb-3 bg-[#4285F4] text-white border-none rounded-sm text-4 font-medium flex items-center justify-center gap-3 hover:bg-[#357ae8]"
              onClick={handleGoogleLogin}
              disabled={loadingGoogle}
              style={{
                cursor: loadingGoogle ? "default" : "pointer",
                opacity: loadingGoogle ? 0.7 : 1
              }}
            >
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M17.64 9.20443C17.64 8.56625..." fill="white" />
              </svg>

              {loadingGoogle
                ? t("providerForm.redirecting")
                : t("providerForm.google")}
            </button>

            {/* SALESFORCE */}
            <button
              onClick={handleSalesforceLogin}
              disabled={!isAuthenticated || loadingSalesforce}
              style={{
                width: "100%",
                padding: "12px 20px",
                marginBottom: "12px",
                backgroundColor: !isAuthenticated ? "#ccc" : "#00A1E0",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor:
                  !isAuthenticated || loadingSalesforce
                    ? "not-allowed"
                    : "pointer",
                opacity: !isAuthenticated || loadingSalesforce ? 0.6 : 1
              }}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="white">
                <path d="M10.006 5.413..." />
              </svg>

              {loadingSalesforce
                ? t("providerForm.redirecting")
                : t("providerForm.salesforce")}
            </button>

            <p>
              {t("providerForm.alreadyAccount")}{" "}
              <Link to="/login">{t("providerForm.signIn")}</Link>
            </p>
          </div>
        </div>
      </div>

      <Copyright />
    </div>
  );
}