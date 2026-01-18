// Homepage.jsx
import Home_Info from "./Home_Info";

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

          <div style={{}}>
            <img
              src="/IMAGE_1.png"
              alt="homepage_image"
              className="h-auto w-300 pt-7.5 pl-7.5"
            />
          </div>
        </div>
      </header>
      
      <Home_Info/>
    </div>
  );
}
