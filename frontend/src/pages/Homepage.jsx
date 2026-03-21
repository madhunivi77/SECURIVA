// Homepage.jsx
import Card from "../components/Card";
import { ChevronRight} from "lucide-react";
import { Link} from "react-router-dom";
import Sponsors from "../components/Sponsors";
import { useState } from "react";

export default function Homepage() {

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

        <div className="pl-20 pr-20 pt-30 pb-30 flex justify-between">
          <div className="pb-5">
            <h1 className="text-xl text-left pt-0 text-white font-mono">The AI Platform that Protects and Automates Your Business</h1>
            <p className="text-[28px] text-left pt-7.5 pb-10 text-blue-600 font-mono">
              <span className="text-white text-bold">SecuriVA</span> unifies <span className="text-white text-bold">AI automation</span>, <span className="text-white text-bold">cybersecurity protection</span>, and <span className="text-white text-bold">secure communication </span>
              into <span className="text-white text-bold">one intelligent platform</span> designed for modern enterprises.
            </p>
            <Link to="/login">
              <button
                className="text-xl w-60 h-17.5 bg-red-500 text-white"
              >
                Start Free Trial
              </button>
            </Link>
          </div>

          <div>
            <div className="overflow-hidden rounded-2xl w-150 mt-7.5 ml-7.5">
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
        <div className="mx-40 mt-20 bg-[#000020]/90 px-8 py-6 rounded-2xl text-white">
          <h2 className="text-[35px] text-center text-white font-mono">Everything your business needs — automated, secured, and connected.</h2>
          <p className="text-center pt-5 text-2xl text-white font-mono" >SecuriVA unifies AI automation, enterprise-grade cybersecurity, and secure AI VPN networking in one intelligent platform. Acting as a 24/7 digital team member, it manages calls, emails, texts, and chats while protecting your domain, website, and data. With built-in eBook creation and seamless integrations across leading business tools, SecuriVA helps organizations operate faster, stay secure, and deliver better customer experiences — all from a single platform.</p>
        </div>
        <div
          id="feature-cards" className="flex flex-wrap justify-center gap-12.5 px-20 pb-20 pt-9 mx-0"
        >
          <Card className={"w-auto sm:w-[25%]"} image={"landing_page/AI_Virtual_assistant.png"} title={"AI Virtual Agent"} text={"Streamline workflows, scheduling, and communications with smart automation tools."}/>
          <Card className={"w-auto sm:w-[25%]"} image={"landing_page/Cybersecurity_Protection.png"} title={"Cybersecurity Protection"} text={"Real-time AI defense for data, users, and digital assets."}/>
          <Card className={"w-auto sm:w-[25%]"} image={"landing_page/AI_VPN.png"} title={"AI VPN"} text={"Secure every connection using adaptive, encrypted networking."}/>
          <Card className={"w-auto sm:w-[25%]"} image={"landing_page/Customer_Interaction.png"} title={"Customer Interaction"} text={"Manage calls, chats, and emails through an intelligent AI avatar."}/>
          <Card className={"w-auto sm:w-[25%]"} image={"landing_page/ebook.png"} title={"eBook Generator"} text={"Instantly create training manuals and awareness guides."}/>
          <Card className={"w-auto sm:w-[25%]"} image={"landing_page/Integrations.png"} title={"Integrations"} text={"Connect with Gmail, Microsoft 365, Salesforce, OpenAI, and more."}/>
        </div>
      </div>

    </div>

      {/* Card Display */}
      
      
      {/* Why Choose SECURIVA */}
      <div className="flex flex-col justify-center section-min-height px-20 pb-10 bg-black text-white">
        <h2 className="text-[40px] pt-7.5 text-center font-mono">Why Choose Us?</h2>
        <p className="text-center px-20 pt-5 pb-9 text-2xl font-mono">SecuriVA brings together AI automation, intelligent virtual assistance, and enterprise-grade cybersecurity in one powerful platform. Designed to integrate seamlessly with your existing tools, SecuriVA protects your business, streamlines operations, and enhances customer interactions through secure, human-like AI. Built with future-ready technologies such as AI-driven VPN and Digital Twin capabilities, SecuriVA helps organizations scale confidently, efficiently, and securely.</p>

        <div className="px-20 flex flex-col text-black">
          <div id="why-cards-wrapper" className="flex flex-1 flex-col justify-center">
            <div id="why-cards" className="flex flex-row gap-5 ">

              <div className="card bg-white shadow-sm why-card">
                <h2 className="text-center text-xl font-medium">All-in-One Platform</h2>
                <figure>
                  <img
                    src="landing_page/aio.png"
                    alt="All-in-One Platform" />
                </figure>

                <p className="text-center">AI automation, cybersecurity, and
                communication in one unified system.</p>
                <div className="flex justify-center">
                  <button className="flex justify-center items-center btn" style={{backgroundColor: "#007bff"}}>
                    Get More
                    <ChevronRight />
                  </button>
                </div>
              </div>

              <div className="card bg-white shadow-sm why-card">
                <h2 className="text-center text-xl font-medium">Intelligent & Human-Like</h2>
                <figure>
                  <img
                    src="landing_page/intelligent.png"
                    alt="Intelligent & Human-Like" />
                </figure>
                
                <p className="text-center">Engage with a smart,
                conversational AI assistant that adapts to your business.</p>
                <div className="flex justify-center">
                  <button className="flex justify-center items-center btn" style={{backgroundColor: "#007bff"}}>
                    Get More
                    <ChevronRight />
                  </button>
                </div>
              </div>

              <div className="card bg-white shadow-sm why-card">
                <h2 className="text-center text-xl font-medium">Seamless Integration</h2>
                <figure>
                  <img
                    src="landing_page/seamless.png"
                    alt="Seamless Integration" />
                </figure>
                <p className="text-center">Works effortlessly with your
                existing tools and cloud services.</p>
                <div className="flex justify-center">
                  <button className="flex justify-center items-center btn" style={{backgroundColor: "#007bff"}}>
                    Get More
                    <ChevronRight />
                  </button>
                </div>
              </div>

              <div className="card bg-white shadow-sm why-card">
                <h2 className="text-center text-xl font-medium">Future Ready</h2>
                <figure>
                  <img
                    src="landing_page/future_ready.png"
                    alt="Future-Ready"
                      />
                </figure>
                <p className="text-center">Powered by AI VPN and Digital Twin
                technology for next-generation innovation.</p>
                <div className="flex justify-center">
                  <button className="flex justify-center items-center btn" style={{backgroundColor: "#007bff"}}>
                    Get More
                    <ChevronRight />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      {/* Text */}
      <div id="demo" className="bg-black text-center text-white pb-10">
          <h2 className="text-3xl">Experience how SecuriVA can Transform Your Business</h2>
          <p className="text-xl/12 pb-5">Transform fragmented security tools into a unified, intelligent defense.</p>
          <button className="text-sm w-50 h-12 bg-red-500 text-white">Request a Demo</button>
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

      <div className="relative mx-40 mt-90 bg-black/50 px-8 py-6 rounded-2xl text-white">
        <h2 className="text-[35px] text-center text-white font-mono">Secure virtual assistant and protection suite ensuring privacy, encrypted communication, and online safety.</h2>
      </div>
    </div>

    <Sponsors className="bg-white pt-5 text-center text-black text-3xl"/>
    {/* ---------- FAQ ---------- */}
      <section className="px-20 pb-20 pt-10">
        <h2 className="text-4xl font-mono text-center mb-12">
          Frequently Asked Questions
        </h2>

        <div className="max-w-4xl mx-auto space-y-4">

          <div className="collapse collapse-arrow bg-[#111633]">
            <input type="checkbox" />
            <div className="collapse-title text-lg font-medium">
              What is SecuriVA?
            </div>
            <div className="collapse-content text-blue-200">
              An AI platform that automates business tasks, enhances customer communication, and provides enterprise-grade cybersecurity.
            </div>
          </div>

          <div className="collapse collapse-arrow bg-[#111633]">
            <input type="checkbox" />
            <div className="collapse-title text-lg font-medium">
              Is SecuriVA secure?
            </div>
            <div className="collapse-content text-blue-200">
              Yes—end-to-end encryption, threat detection, and compliance with GDPR, HIPAA, and PCI-DSS.
            </div>
          </div>

          <div className="collapse collapse-arrow bg-[#111633]">
            <input type="checkbox" />
            <div className="collapse-title text-lg font-medium">
              Can SecuriVA integrate with my tools?
            </div>
            <div className="collapse-content text-blue-200">
              Yes. SecuriVA connects to Gmail, WhatsApp, Salesforce, APIs, and many more platforms.
            </div>
          </div>

          <div className="collapse collapse-arrow bg-[#111633]">
            <input type="checkbox" />
            <div className="collapse-title text-lg font-medium">
              Who can use SecuriVA?
            </div>
            <div className="collapse-content text-blue-200">
              SMEs, enterprises, fintech, healthcare, education, e-commerce, and professionals needing automation.
            </div>
          </div>

          <div className="collapse collapse-arrow bg-[#111633]">
            <input type="checkbox" />
            <div className="collapse-title text-lg font-medium">
              Do you offer customer support?
            </div>
            <div className="collapse-content text-blue-200">
              Yes—24/7 support, onboarding, and detailed documentation.
            </div>
          </div>
        </div>
        <div className="flex justify-center pt-5">
          <Link to="/FAQ"><button className="text-lg w-50 h-12 bg-red-500 text-white">More FAQs</button></Link>
        </div>
      </section>

      {/* ---------- NEWSLETTER SUBSCRIPTION ---------- */}
      <section className="py-20 px-10 bg-white dark:bg-gray-800">
        <div className="max-w-4xl mx-auto">

          <h2 className="text-3xl font-bold text-center">
            Subscribe to Our Newsletter
          </h2>

          <p className="text-xl text-center mb-4 mt-8">Enter your email to receive smarter security insights directly in your inbox.</p>

          <form onSubmit={handleSubmit} className="space-y-6">

            <div className="flex flex-col items-center gap-6">

              <input
                name="email"
                value={formData.email}
                onChange={handleChange}
                type="email"
                placeholder="Email Address"
                className="input input-bordered w-150"
                required
              />

              <button className="btn btn-primary w-50">Subscribe</button>

            </div>

          </form>
        </div>
      </section>
    </div>
  );
}
