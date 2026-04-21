import { Link, useNavigate } from "react-router-dom";
import { ChevronLeft } from "lucide-react";
import Copyright from "../components/Copyright";
import { useTranslation } from "react-i18next";

export default function SignupForm() {
  const navigate = useNavigate();
  const { t } = useTranslation();

  return (
    <div className="bg-[#000020] w-screen min-h-screen flex flex-col justify-between">
      <div>
        <button
          onClick={() => navigate(-1)}
          className="text-white absolute top-0 left-0"
        >
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
          <form className="flex flex-col pr-0 md:pr-10 mx-auto md:mx-0 md:max-w-none w-auto md:w-[35%] justify-center pt-10 font-sans text-white">

            <img src="LOGO_FOOTER_0000.png" className="pb-5 w-45 mx-auto" />

            <h2 className="text-2xl font-semibold">
              {t("signupForm.title")}
            </h2>

            <p className="mb-6">
              {t("signupForm.subtitle")}
            </p>

            <input
              className="input validator bg-slate-800 border-black text-white mb-3 w-full"
              type="email"
              required
              placeholder={t("signupForm.email")}
            />

            <input
              type="tel"
              className="input validator tabular-nums bg-slate-800 border-black text-white mb-3 w-full"
              required
              placeholder={t("signupForm.phone")}
              pattern="[0-9]*"
              minLength="10"
              maxLength="10"
              title="Must be 10 digits"
            />

            <input
              className="input bg-slate-800 border-black text-white mb-3 w-full"
              type="password"
              required
              placeholder={t("signupForm.password")}
              minLength="8"
              pattern="(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}"
              title="Must include number, lowercase and uppercase letter"
            />

            <input
              className="input bg-slate-800 border-black text-white mb-3 w-full"
              type="password"
              required
              placeholder={t("signupForm.confirmPassword")}
            />

            <p>
              <input
                id="tos"
                type="checkbox"
                className="checkbox checkbox-info"
                required
              />{" "}
              {t("signupForm.terms")}
            </p>

            {/* BUTTON */}
            <button
              className="w-full px-3 py-5 my-3 bg-[#4285F4] text-white border-none rounded-sm text-4 font-medium flex items-center justify-center gap-3 hover:bg-[#357ae8]"
              type="submit"
            >
              {t("signupForm.button")}
            </button>

            <p>
              {t("signupForm.alreadyAccount")}{" "}
              <Link to="/login">{t("signupForm.signIn")}</Link>
            </p>
          </form>
        </div>
      </div>

      <Copyright />
    </div>
  );
}