// Homepage.jsx
import Card from "./Card";

export default function Homepage() {

  return (
    <div className="homepage">

      {/* ---------- HEADER ---------- */}
      <header className="hero section-min-height">

        <div className="hero-content flex justify-evenly">
          <div>
            <h1 className="text-xl text-left pt-5">THE AI PLATFORM THAT PROTECTS AND AUTOMATES YOUR BUSINESS</h1>
            <p className="text-m text-left pt-7.5 pb-10">
              SecuriVA unifies AI automation, cybersecurity protection, and secure communication
              into one intelligent platform designed for modern enterprises.
            </p>
            <button
              className="text-sm w-50 h-17.5 bg-red-500"
            >
              Start Free Trial
            </button>
          </div>

          <div>
            <img
              src="/IMAGE_1.png"
              alt="homepage_image"
              className="h-auto w-300 pt-7.5 pl-7.5"
            />
          </div>
        </div>
      </header>
      
      <div className="info">
        <div
            className="gap-12.5 p-20 mx-0 my-auto text-black"
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(3, 1fr)"
            }}
          >
            <Card image={"/AI_Virtual_assistant.png"} title={"AI Virtual Agent"} text={"Streamline workflows, scheduling, and communications with smart automation tools."}/>
            <Card image={"/Cybersecurity_Protection.png"} title={"Cybersecurity Protection"} text={"Real-time AI defense for data, users, and digital assets."}/>
            <Card image={"/AI_VPN.png"} title={"AI VPN"} text={"Secure every connection using adaptive, encrypted networking."}/>
            <Card image={"/Customer_Interaction.png"} title={"Customer Interaction"} text={"Manage calls, chats, and emails through an intelligent AI avatar."}/>
            <Card image={"/ebook.png"} title={"eBook Generator"} text={"Instantly create training manuals and awareness guides."}/>
            <Card image={"/Integrations.png"} title={"Integrations"} text={"Connect with Gmail, Microsoft 365, Salesforce, OpenAI, and more."}/>
          </div>
          
          <h2
            className="text-[40px] pt-7.5"
          >
            💼 Why Choose SecuriVA
          </h2>
          <ul>
            <li>
              <strong>All-in-One Platform:</strong> AI automation, cybersecurity, and
              communication in one unified system.
            </li>
            <li>
              <strong>Enterprise-Grade Security:</strong> Built for complete protection
              with encrypted AI-driven systems.
            </li>
            <li>
              <strong>Intelligent & Human-Like:</strong> Engage with a smart,
              conversational AI assistant that adapts to your business.
            </li>
            <li>
              <strong>Seamless Integration:</strong> Works effortlessly with your
              existing tools and cloud services.
            </li>
            <li>
              <strong>Future-Ready:</strong> Powered by AI VPN and Digital Twin
              technology for next-generation innovation.
            </li>
          </ul>
      </div>
    </div>
  );
}
