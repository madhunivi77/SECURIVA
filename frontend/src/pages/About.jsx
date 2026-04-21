// About.jsx
import Sponsors from "../components/Sponsors";
import Card from "../components/Card";
import { useTranslation } from "react-i18next";

export default function About() {
  const { t } = useTranslation();
  
  return (
    <div className="min-h-screen bg-[#0a0f1f]">

      {/* ---------- HERO ---------- */}
      <section className="hero py-24 text-white">
        <div className="hero-content text-center max-w-4xl">
          <div>
            <h1 className="text-5xl font-bold mb-6">{t("about.hero.title")}</h1>
            <p className="text-xl opacity-90">
              {t("about.hero.description")}
            </p>
          </div>
        </div>
      </section>

      {/* ---------- COMPANY STORY ---------- */}
      <section className="relative pt-20 mx-auto overflow-hidden">

        <div className="relative w-full min-h-screen overflow-hidden bg-black mx-auto">
          <video
            autoPlay
            loop
            muted
            playsInline
            className="absolute top-0 left-0 w-full h-full object-cover opacity-50"
          >
            <source src="/landing_page/banner.mp4" type="video/mp4" />
            Your browser does not support the video tag.
          </video>

          <div className="absolute top-0 left-0 w-full h-64 bg-gradient-to-b from-[#0a0f1f] via-[#0a0f1f]/60 to-transparent pointer-events-none"></div>

          <div className="absolute bottom-0 left-0 w-full h-64 bg-gradient-to-t from-black via-black/60 to-transparent pointer-events-none"></div>

          <div className="relative z-5 flex flex-col md:flex-row items-center justify-center gap-8 px-6 py-20">
            <div className="card shadow-xl bg-white/90 backdrop-blur dark:bg-gray-800/90 max-h-200 max-w-200">
              <div className="card-body  text-xl">
                <h3 className="card-title text-3xl font-bold text-gray-900 dark:text-white mb-6">
                  {t("about.story.title")}
                </h3>

                <p className="text-gray-700 dark:text-gray-300 mb-4">
                  {t("about.story.p1")}
                </p>

                <p className="text-gray-700 dark:text-gray-300 mb-4">
                  {t("about.story.p2")}
                </p>

                <p className="text-gray-700 dark:text-gray-300">
                  {t("about.story.p3")}
                </p>
              </div>
            </div>

            <div className="card shadow-xl bg-white/90 backdrop-blur dark:bg-gray-800/90 min-h-110 max-h-200 max-w-200">
              <div className="card-body">
                <h3 className="card-title">{t("about.enterprise.title")}</h3>
                <ul className="space-y-3 text-gray-600 dark:text-gray-300 text-xl">
                  <li>• {t("about.enterprise.features.ai_assistant")}</li>
                  <li>• {t("about.enterprise.features.threat_detection")}</li>
                  <li>• {t("about.enterprise.features.secure_networking")}</li>
                  <li>• {t("about.enterprise.features.communication")}</li>
                  <li>• {t("about.enterprise.features.integrations")}</li>
                </ul>
              </div>
            </div>
          </div>

        </div>

      </section>

      {/* ---------- MISSION / VISION / VALUES ---------- */}
      <section className="bg-black">
        <div className="max-w-6xl mx-auto">

          <h2 className="text-5xl font-bold text-center text-gray-900 dark:text-white mb-12">
            {t("about.principles.title")}
          </h2>

          <div className="grid md:grid-cols-3 gap-8">

            <div className="card shadow-lg">
              <div className="card-body text-xl">
                <h3 className="card-title text-xl">{t("about.principles.mission.title")}</h3>
                <p>
                  {t("about.principles.mission.text")}
                </p>
              </div>
            </div>

            <div className="card shadow-lg">
              <div className="card-body text-xl">
                <h3 className="card-title text-xl">{t("about.principles.vision.title")}</h3>
                <p>
                  {t("about.principles.vision.text")}
                </p>
              </div>
            </div>

            <div className="card shadow-lg">
              <div className="card-body text-xl">
                <h3 className="card-title text-xl">{t("about.principles.values.title")}</h3>
                <ul className="space-y-2">
                  <li>• {t("about.principles.values.items.security")}</li>
                  <li>• {t("about.principles.values.items.ai")}</li>
                  <li>• {t("about.principles.values.items.privacy")}</li>
                  <li>• {t("about.principles.values.items.reliability")}</li>
                  <li>• {t("about.principles.values.items.improvement")}</li>
                </ul>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* ---------- PLATFORM OVERVIEW ---------- */}
      <section className="bg-black">
        <div className="mx-auto text-black">

          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12 pt-10">
            {t("about.platform.title")}
          </h2>

          <div
            id="feature-cards"
            className="flex flex-wrap justify-center gap-12.5 pb-20 pt-9 mx-0"
          >

            <Card
              className={"w-auto sm:w-[25%]"}
              image={"landing_page/AI_Virtual_assistant.png"}
              title={t("about.platform.features.ai_agent.title")}
              text={t("about.platform.features.ai_agent.text")}
            />

            <Card
              className={"w-auto sm:w-[25%]"}
              image={"landing_page/Cybersecurity_Protection.png"}
              title={t("about.platform.features.cybersecurity.title")}
              text={t("about.platform.features.cybersecurity.text")}
            />

            <Card
              className={"w-auto sm:w-[25%]"}
              image={"landing_page/AI_VPN.png"}
              title={t("about.platform.features.vpn.title")}
              text={t("about.platform.features.vpn.text")}
            />

            <Card
              className={"w-auto sm:w-[25%]"}
              image={"landing_page/Customer_Interaction.png"}
              title={t("about.platform.features.customer_ai.title")}
              text={t("about.platform.features.customer_ai.text")}
            />

            <Card
              className={"w-auto sm:w-[25%]"}
              image={"landing_page/ebook.png"}
              title={t("about.platform.features.ebook.title")}
              text={t("about.platform.features.ebook.text")}
            />

            <Card
              className={"w-auto sm:w-[25%]"}
              image={"landing_page/Integrations.png"}
              title={t("about.platform.features.integrations.title")}
              text={t("about.platform.features.integrations.text")}
            />

          </div>
        </div>
      </section>

      {/* ---------- HOW IT WORKS ---------- */}
      <section className="py-20 px-10 bg-white dark:bg-gray-800">
        <div className="max-w-5xl mx-auto text-center">

          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-10">
            {t("about.howItWorks.title")}
          </h2>

          <div className="steps steps-vertical md:steps-horizontal w-full">

            <div className="step step-primary">
              {t("about.howItWorks.steps.step1")}
            </div>

            <div className="step step-primary">
              {t("about.howItWorks.steps.step2")}
            </div>

            <div className="step step-primary">
              {t("about.howItWorks.steps.step3")}
            </div>

            <div className="step step-primary">
              {t("about.howItWorks.steps.step4")}
            </div>

          </div>

        </div>
      </section>
      <Sponsors className="bg-white pt-5 text-center text-black text-3xl" />
    </div>
  );
}
