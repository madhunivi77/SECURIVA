import { Link, useNavigate } from "react-router-dom";
import { ChevronLeft } from "lucide-react";
import Copyright from "../components/Copyright";

export default function SignupForm() {
  const navigate = useNavigate();

  return (
    <div className="bg-[#000020] w-screen min-h-screen flex flex-col justify-between">
      <div>
        <button onClick={() => navigate(-1)} className="text-white absolute top-0 left-0"><ChevronLeft /></button>
        <div className="flex flex-col-reverse md:flex-row justify-center gap-10 text-center">
          <div className="flex flex-col justify-center w-auto md:w-[40%] pt-0 md:pt-20">
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
          <form className="flex flex-col pr-0 md:pr-10 mx-auto md:mx-0 md:max-w-none w-auto md:w-[35%] justify-center pt-10 font-sans text-white">
            <img src="LOGO_FOOTER_0000.png" className="pb-5 w-45 mx-auto"/>
            <h2 className=" text-2xl font-semibold">Create your account</h2>
            <p className="mb-6">
              Fill in your details to get started with Securiva.
            </p>
      
            <input id="email" className="input validator bg-slate-800 border-black text-white mb-3 w-full" type="email" required placeholder="Email" />
            <input id="phone" type="tel" className="input validator tabular-nums bg-slate-800 border-black text-white mb-3 w-full" required placeholder="Phone" 
              pattern="[0-9]*" minLength="10" maxLength="10" title="Must be 10 digits" />
            <input id="password" className="input bg-slate-800 border-black text-white mb-3 w-full" type="password" required placeholder="Password" minLength="8" 
              pattern="(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}" 
              title="Must be more than 8 characters, including number, lowercase letter, uppercase letter"/>
            <input className="input bg-slate-800 border-black text-white mb-3 w-full" type="password" required placeholder="Password" />
            <p className=""><input id="tos" type="checkbox" className="checkbox checkbox-info" required/> I agree to the Terms of Service and Privacy Policy</p>
            {/* Signin Button */}
            <button
              //onClick={}
              className="w-full px-3 py-5 my-3 bg-[#4285F4] text-white border-none rounded-sm text-4 font-medium flex items-center justify-center gap-3 hover:bg-[#357ae8]"
              type="submit"
            >
              Create account
            </button>
            <p className="">Already have an account? <Link to="/login">Sign In</Link></p>
          </form>
        </div>
      </div>
      <Copyright />
    </div>
  );
}
