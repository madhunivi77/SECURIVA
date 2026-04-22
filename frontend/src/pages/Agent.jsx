import { ChevronRight} from "lucide-react";
import { useTheme } from "../context/ThemeContext";
import { useTranslation } from "react-i18next";
function Agent() {
    const { t } = useTranslation();
    const {theme} = useTheme();
    return (
        <div>
            <header className="hero section-min-height">
                <div className="hero-content flex justify-evenly">
                    <div>
                        <h1 className="text-[40px] text-left pt-5">{t("agent.hero.title")}</h1>
                        <p className="text-[25px] text-left pt-7.5 pb-10">
                            {t("agent.hero.description")}
                        </p>
                        <button
                            className="font-[20px] w-50 h-17.5 bg-red-500"
                        >
                            {t("agent.hero.cta")}
                        </button>
                    </div>

                    <div style={{}}>
                        <img
                            src="/agent.png"
                            alt="agent_page_image"
                            className="h-auto w-300 px-7.5 py-7.5"
                        />
                    </div>
                </div>
            </header>
            <div className="section-min-height">
                <h2 className="text-center text-3xl pb-5" style={{color: theme.text}}>{t("agent.intro.title")}</h2>
                {/* Communication Channels */}
                <div className="flex flex-col justify-center lg:flex-row mx-[10%]" style={{color: theme.text}}>
                    <div className="card card-side bg-base-100 shadow-sm h-100">
                        <figure>
                            <img
                            src="/agent_page/voice.png"
                            alt="Voice" 
                            className="w-2/3"/>
                        </figure>
                        <div className="card-body w-1/3">
                            <h2 className="card-title">{t("agent.interfaces.voice.title")}</h2>
                            <p>{t("agent.interfaces.voice.description")}</p>
                            <div className="card-actions justify-end">
                            <button className="btn btn-primary">{t("agent.interfaces.voice.cta")}<ChevronRight /></button>
                            </div>
                        </div>
                    </div>

                    <div className="divider lg:divider-horizontal" >{t("agent.interfaces.divider")}</div>

                    <div className="card card-side bg-base-100 shadow-sm h-100">
                        <figure>
                            <img
                            src="/agent_page/text.png"
                            alt="Chatbot"
                            className="w-2/3" />
                        </figure>
                        <div className="card-body w-1/3">
                            <h2 className="card-title">{t("agent.interfaces.chat.title")}</h2>
                            <p>{t("agent.interfaces.chat.description")}</p>
                            <div className="card-actions justify-end">
                            <button className="btn btn-primary">{t("agent.interfaces.chat.cta")}<ChevronRight /></button>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
            <div className="mb-10">
                <h2 className="text-center text-3xl pb-5" style={{color: theme.text}}>{t("agent.productivity.title")}</h2>
                {/* Graph */}
                <img className="section-max-height mx-auto" src="/agent_page/Graph.png"></img>
            </div>
        </div>
    )
}

export default Agent;