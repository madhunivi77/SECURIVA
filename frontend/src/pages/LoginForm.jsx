import { Link, useNavigate } from "react-router-dom";
import { ChevronLeft } from "lucide-react";
import Copyright from "../components/Copyright";
import { useTranslation } from "react-i18next";

export default function LoginForm() {
  const navigate = useNavigate();
  const { t } = useTranslation();

  return (
    <div className="bg-[#000020] w-screen min-h-screen flex flex-col relative">

      {/* Back Button */}
      <button
        onClick={() => navigate(-1)}
        className="text-white absolute top-4 left-4 z-10"
      >
        <ChevronLeft size={32} />
      </button>

      {/* Center Section */}
      <div className="flex-1 flex flex-col justify-center">

        <div className="flex flex-col-reverse md:flex-row justify-center items-center gap-10 text-center px-6">

          {/* Video */}
          <div className="flex flex-col justify-center w-auto md:w-[40%]">
            <video autoPlay loop muted playsInline className="w-full rounded-lg">
              <source src="/landing_page/SecurivaHero.mp4" type="video/mp4" />
            </video>
          </div>

          {/* Form */}
          <div className="flex flex-col w-full max-w-md justify-center font-sans">

            <img
              src="LOGO_FOOTER_0000.png"
              className="pb-5 w-40 mx-auto"
              alt="Logo"
            />

            <h2 className="text-2xl font-semibold text-white">
              {t("login.welcome")}
            </h2>

            <p className="mb-6 text-gray-300">
              {t("login.subtitle")}
            </p>

            <input
              className="input bg-slate-800 border-black text-white mb-3 w-full"
              type="email"
              required
              placeholder={t("login.email")}
            />

            <input
              className="input bg-slate-800 border-black text-white mb-3 w-full"
              type="password"
              required
              placeholder={t("login.password")}
            />

            <p className="text-right text-sm text-gray-400 hover:text-white cursor-pointer">
              {t("login.forgotPassword")}
            </p>

            <button className="w-full px-3 py-4 my-4 bg-[#4285F4] text-white rounded-sm font-medium flex items-center justify-center gap-3 hover:bg-[#357ae8] transition-colors">
              {t("login.signIn")}
            </button>

            <p className="text-gray-300">
              {t("login.noAccount")}{" "}
              <Link to="/signup" className="text-blue-400 hover:text-blue-300">
                {t("login.createAccount")}
              </Link>
            </p>

          </div>
        </div>
      </div>

      {/* Footer */}
      <Copyright />
    </div>
  );
}