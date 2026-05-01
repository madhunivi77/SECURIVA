// Homepage.jsx
import Card from "../components/Card";
import { ChevronRight} from "lucide-react";
import { Link} from "react-router-dom";
import Sponsors from "../components/Sponsors";
import { useState } from "react";
import { useTranslation } from "react-i18next";

export default function Homepage() {
  const { t } = useTranslation();

  const [formData, setFormData] = useState({
      name: "",
      email: "",
      company: "",
      type: "general",
      message: "",
    });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    alert("Thank you for subscribing!");
    setFormData({
      email: "",
    });
  };

  return (
    <div id="homepage">

      {/* ---------- HERO ---------- */}
      <header className="hero">

        <div className="lg:px-20 pt-10 pb-30 flex lg:flex-row flex-col justify-center lg:justify-between items-center lg:items-start">
          <div className="pb-5 flex flex-col items-center lg:items-start px-5 lg:px-0">
            <h1 className="text-xl text-center lg:text-left pt-0 text-white font-mono">{t("homepage.hero.title")}</h1>
            <p className="text-[28px] text-center lg:text-left pt-7.5 pb-10 text-blue-600 font-mono">
              <span className="text-white text-bold">{t("homepage.hero.brand")}</span> {t("homepage.hero.unifies")} <span className="text-white text-bold">{t("homepage.hero.aiAutomation")}</span>, <span className="text-white text-bold">{t("homepage.hero.cybersecurity")}</span>, <span className="text-white text-bold">{t("homepage.hero.secureCommunication")} </span>
              {t("homepage.hero.into")} <span className="text-white text-bold">{t("homepage.hero.platform")}</span> {t("homepage.hero.tail")}
            </p>
            <Link to="/login">
              <button
                className="text-xl w-60 h-17.5 bg-red-500 text-white "
              >
                {t("homepage.hero.cta")}
              </button>
            </Link>
          </div>

          <div className="flex justify-center">
            <div className="overflow-hidden rounded-2xl w-[90%] lg:w-150 mt-7.5 lg:ml-7.5">
              <video
                autoPlay
                loop
                muted
                playsInline
              >
                <source src="/landing_page/SecurivaHero.mp4" type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            </div>
          </div>
        </div>
      </header>
      
      {/* Video */}
      <div className="relative w-full min-h-screen overflow-hidden bg-black">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="absolute top-0 left-0 w-full h-full object-cover"
        >
          <source src="/landing_page/banner.mp4" type="video/mp4" />
          Your browser does not support the video tag.
      </video>

      <div className="absolute top-0 left-0 w-full h-64 bg-gradient-to-b from-[#0a0f1f] via-[#0a0f1f]/60 to-transparent pointer-events-none"></div>

      <div className="absolute bottom-0 left-0 w-full h-64 bg-gradient-to-t from-black via-black/60 to-transparent pointer-events-none"></div>

      <div id="feature-cards-wrapper" className="relative section-min-height text-center text-black">
        <div className="mx-5 lg:mx-40 mt-20 bg-[#000020]/90 px-8 py-6 rounded-2xl text-white">
          <h2 className="text-[35px] text-center text-white font-mono">{t("homepage.overview.title")}</h2>
          <p className="text-center pt-5 text-2xl text-white font-mono" >{t("homepage.overview.description")}</p>
        </div>
        <div
          id="feature-cards" className="flex flex-wrap justify-center gap-12.5 px-5 lg:px-20 pb-20 pt-9 mx-0"
        >
          <Card className={"w-auto sm:w-[25%]"} image={"landing_page/AI_Virtual_assistant.png"} title={t("homepage.cards.aiAgent.title")} text={t("homepage.cards.aiAgent.description")}/>
          <Card className={"w-auto sm:w-[25%]"} image={"landing_page/Cybersecurity_Protection.png"} title={t("homepage.cards.cybersecurity.title")} text={t("homepage.cards.cybersecurity.description")}/>
          <Card className={"w-auto sm:w-[25%]"} image={"landing_page/AI_VPN.png"} title={t("homepage.cards.vpn.title")} text={t("homepage.cards.vpn.description")}/>
          <Card className={"w-auto sm:w-[25%]"} image={"landing_page/Customer_Interaction.png"} title={t("homepage.cards.customerInteraction.title")} text={t("homepage.cards.customerInteraction.description")}/>
          <Card className={"w-auto sm:w-[25%]"} image={"landing_page/ebook.png"} title={t("homepage.cards.ebook.title")} text={t("homepage.cards.ebook.description")}/>
          <Card className={"w-auto sm:w-[25%]"} image={"landing_page/Integrations.png"} title={t("homepage.cards.integrations.title")} text={t("homepage.cards.integrations.description")}/>
        </div>
      </div>

    </div>

      {/* Card Display */}
      
      
      {/* Why Choose SECURIVA */}
      <div className="flex flex-col justify-center items-center lg:items-stretch section-min-height lg:px-20 pb-10 bg-black text-white">
        <h2 className="text-[40px] pt-7.5 text-center font-mono">{t("homepage.why.title")}</h2>
        <p className="text-center px-20 lg:px-20 pt-5 pb-9 text-2xl font-mono">{t("homepage.why.description")}</p>

        <div className="px-20 flex flex-col text-black">
          <div id="why-cards-wrapper" className="flex flex-1 flex-col justify-center">
            <div id="why-cards" className="flex flex-col lg:flex-row gap-5 ">

              <div className="card bg-white shadow-sm why-card">
                <h2 className="text-center text-xl font-medium">{t("homepage.why.cards.allInOne.title")}</h2>
                <figure>
                  <img
                    src="landing_page/aio.png"
                    alt={t("homepage.why.cards.allInOne.title")} />
                </figure>

                <p className="text-center">{t("homepage.why.cards.allInOne.description")}</p>
                <div className="flex justify-center">
                  <button className="flex justify-center items-center btn" style={{backgroundColor: "#007bff"}}>
                    {t("homepage.why.getMore")}
                    <ChevronRight />
                  </button>
                </div>
              </div>

              <div className="card bg-white shadow-sm why-card">
                <h2 className="text-center text-xl font-medium">{t("homepage.why.cards.intelligent.title")}</h2>
                <figure>
                  <img
                    src="landing_page/intelligent.png"
                    alt={t("homepage.why.cards.intelligent.title")} />
                </figure>
                
                <p className="text-center">{t("homepage.why.cards.intelligent.description")}</p>
                <div className="flex justify-center">
                  <button className="flex justify-center items-center btn" style={{backgroundColor: "#007bff"}}>
                    {t("homepage.why.getMore")}
                    <ChevronRight />
                  </button>
                </div>
              </div>

              <div className="card bg-white shadow-sm why-card">
                <h2 className="text-center text-xl font-medium">{t("homepage.why.cards.integration.title")}</h2>
                <figure>
                  <img
                    src="landing_page/seamless.png"
                    alt={t("homepage.why.cards.integration.title")} />
                </figure>
                <p className="text-center">{t("homepage.why.cards.integration.description")}</p>
                <div className="flex justify-center">
                  <button className="flex justify-center items-center btn" style={{backgroundColor: "#007bff"}}>
                    {t("homepage.why.getMore")}
                    <ChevronRight />
                  </button>
                </div>
              </div>

              <div className="card bg-white shadow-sm why-card">
                <h2 className="text-center text-xl font-medium">{t("homepage.why.cards.future.title")}</h2>
                <figure>
                  <img
                    src="landing_page/future_ready.png"
                    alt={t("homepage.why.cards.future.title")}
                      />
                </figure>
                <p className="text-center">{t("homepage.why.cards.future.description")}</p>
                <div className="flex justify-center">
                  <button className="flex justify-center items-center btn" style={{backgroundColor: "#007bff"}}>
                    {t("homepage.why.getMore")}
                    <ChevronRight />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      {/* Text */}
      <div id="demo" className="bg-black text-center text-white pb-10 px-5 lg:px-0">
          <h2 className="text-3xl">{t("homepage.demo.title")}</h2>
          <p className="text-xl/12 pb-5">{t("homepage.demo.description")}</p>
          <button className="text-sm w-50 h-12 bg-red-500 text-white">{t("homepage.demo.button")}</button>
      </div>
      
      {/* Video */}
      <div className="relative w-full min-h-screen overflow-hidden bg-black">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="absolute top-0 left-0 w-full h-full object-cover"
        >
          <source src="/landing_page/LandingVideo.mp4" type="video/mp4" />
          Your browser does not support the video tag.
      </video>

      <div className="relative mx-5 lg:mx-40 mt-90 bg-black/50 px-8 py-6 rounded-2xl text-white">
        <h2 className="text-[35px] text-center text-white font-mono">{t("homepage.video.bannerText")}</h2>
      </div>
    </div>

    <Sponsors className="bg-white pt-5 text-center text-black text-3xl"/>
    {/* ---------- FAQ ---------- */}
      <section className="px-20 pb-20 pt-10">
        <h2 className="text-4xl font-mono text-center mb-12">
          {t("homepage.faq.title")}
        </h2>

        <div className="max-w-4xl mx-auto space-y-4">

          <div className="collapse collapse-arrow bg-[#111633]">
            <input type="checkbox" />
            <div className="collapse-title text-lg font-medium">
              {t("homepage.faq.items.0.question")}
            </div>
            <div className="collapse-content text-blue-200">
              {t("homepage.faq.items.0.answer")}
            </div>
          </div>

          <div className="collapse collapse-arrow bg-[#111633]">
            <input type="checkbox" />
            <div className="collapse-title text-lg font-medium">
              {t("homepage.faq.items.1.question")}
            </div>
            <div className="collapse-content text-blue-200">
              {t("homepage.faq.items.1.answer")}
            </div>
          </div>

          <div className="collapse collapse-arrow bg-[#111633]">
            <input type="checkbox" />
            <div className="collapse-title text-lg font-medium">
              {t("homepage.faq.items.2.question")}
            </div>
            <div className="collapse-content text-blue-200">
              {t("homepage.faq.items.2.answer")}
            </div>
          </div>

          <div className="collapse collapse-arrow bg-[#111633]">
            <input type="checkbox" />
            <div className="collapse-title text-lg font-medium">
              {t("homepage.faq.items.3.question")}
            </div>
            <div className="collapse-content text-blue-200">
              {t("homepage.faq.items.3.answer")}
            </div>
          </div>

          <div className="collapse collapse-arrow bg-[#111633]">
            <input type="checkbox" />
            <div className="collapse-title text-lg font-medium">
              {t("homepage.faq.items.4.question")}
            </div>
            <div className="collapse-content text-blue-200">
              {t("homepage.faq.items.4.answer")}
            </div>
          </div>
        </div>
        <div className="flex justify-center pt-5">
          <Link to="/FAQ"><button className="text-lg w-50 h-12 bg-red-500 text-white">{t("homepage.faq.moreButton")}</button></Link>
        </div>
      </section>

      {/* ---------- NEWSLETTER SUBSCRIPTION ---------- */}
      <section className="py-20 px-10 bg-gray-800">
        <div className="max-w-4xl mx-auto">

          <h2 className="text-3xl font-bold text-center">
            {t("homepage.newsletter.title")}
          </h2>

          <p className="text-xl text-center mb-4 mt-8">{t("homepage.newsletter.description")}</p>

          <form onSubmit={handleSubmit} className="space-y-6">

            <div className="flex flex-col items-center gap-6">

              <input
                name="email"
                value={formData.email}
                onChange={handleChange}
                type="email"
                placeholder="Email Address"
                className="input input-bordered w-[95%] lg:w-150"
                required
              />

              <button className="btn btn-primary w-50">{t("homepage.newsletter.button")}</button>

            </div>

          </form>
        </div>
      </section>
    </div>
  );
}
