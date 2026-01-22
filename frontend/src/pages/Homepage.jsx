// Homepage.jsx
import Card from "../components/Card";
export default function Homepage() {

  return (
    <div id="homepage">

      {/* ---------- HERO ---------- */}
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
              src="landing_page/IMAGE_1.png"
              alt="homepage_image"
              className="h-auto w-300 pt-7.5 pl-7.5"
            />
          </div>
        </div>
      </header>
      
      {/* Card Display */}
      <div id="feature-cards-wrapper" className="section-min-height text-black bg-gray-200">
        <h2 className="text-[40px] pt-7.5 text-center">Key Features</h2>
        <div
          id="feature-cards" className="gap-12.5 p-20 mx-0 my-auto"
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)"
          }}
        >
          <Card image={"landing_page/AI_Virtual_assistant.png"} title={"AI Virtual Agent"} text={"Streamline workflows, scheduling, and communications with smart automation tools."}/>
          <Card image={"landing_page/Cybersecurity_Protection.png"} title={"Cybersecurity Protection"} text={"Real-time AI defense for data, users, and digital assets."}/>
          <Card image={"landing_page/AI_VPN.png"} title={"AI VPN"} text={"Secure every connection using adaptive, encrypted networking."}/>
          <Card image={"landing_page/Customer_Interaction.png"} title={"Customer Interaction"} text={"Manage calls, chats, and emails through an intelligent AI avatar."}/>
          <Card image={"landing_page/ebook.png"} title={"eBook Generator"} text={"Instantly create training manuals and awareness guides."}/>
          <Card image={"landing_page/Integrations.png"} title={"Integrations"} text={"Connect with Gmail, Microsoft 365, Salesforce, OpenAI, and more."}/>
        </div>
      </div>
      
      {/* Why Choose SECURIVA */}
      <div className="section-min-height px-20 flex flex-col bg-gray-200 text-black">
        <h2 className="text-[40px] pt-7.5 text-center">Why Choose SecuriVA?</h2>
        <div id="why-cards-wrapper" className="flex flex-1 flex-col justify-center">
          <div id="why-cards" className="flex flex-row gap-5 ">
            <div className="card card-side bg-white shadow-sm why-card">
              <figure>
                <img
                  src="landing_page/aio.png"
                  alt="All-in-One Platform" />
              </figure>
              <div className="card-body">
                <h2 className="card-title">All-in-One Platform</h2>
                <p>AI automation, cybersecurity, and
                communication in one unified system.</p>
                <div className="card-actions justify-end">
                  <button className="btn btn-primary">More</button>
                </div>
              </div>
            </div>

            <div className="card card-side bg-white shadow-sm why-card">
              <figure>
                <img
                  src="landing_page/intelligent.png"
                  alt="Intelligent & Human-Like" />
              </figure>
              <div className="card-body">
                <h2 className="card-title">Intelligent & Human-Like</h2>
                <p>Engage with a smart,
                conversational AI assistant that adapts to your business.</p>
                <div className="card-actions justify-end">
                  <button className="btn btn-primary">More</button>
                </div>
              </div>
            </div>

            <div className="card card-side bg-white shadow-sm why-card">
              <figure>
                <img
                  src="landing_page/seamless.png"
                  alt="Seamless Integration" />
              </figure>
              <div className="card-body">
                <h2 className="card-title">Seamless Integration</h2>
                <p>Works effortlessly with your
                existing tools and cloud services.</p>
                <div className="card-actions justify-end">
                  <button className="btn btn-primary">More</button>
                </div>
              </div>
            </div>

            <div className="card card-side bg-white shadow-sm why-card">
              <figure>
                <img
                  src="landing_page/future_ready.png"
                  alt="Future-Ready" />
              </figure>
              <div className="card-body">
                <h2 className="card-title">Future-Ready</h2>
                <p>Powered by AI VPN and Digital Twin
                technology for next-generation innovation.</p>
                <div className="card-actions justify-end">
                  <button className="btn btn-primary">More</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      {/* Text */}
      <div id="demo" className="bg-gray-200 text-center text-black section-min-height p-20">
          <h2 className="text-3xl">Experience how SecuriVA can Transform Your Business</h2>
          <p className="text-xl/12">Transform fragmented security tools into a unified, intelligent defense.</p>
          <button className="text-sm w-50 h-12 bg-blue-500 text-white">Request a Demo</button>
      </div>

    </div>
  );
}
