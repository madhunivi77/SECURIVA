import { Link, useNavigate } from "react-router-dom";
import { ChevronLeft } from "lucide-react";

export default function LoginForm() {

  const navigate = useNavigate();

  return (
    <div className="bg-white w-screen min-h-screen">
      <button onClick={() => navigate(-1)} className="text-black"><ChevronLeft /></button>
      <div className="flex flex-col-reverse md:flex-row justify-center gap-5 text-center bg-white">
        <div className="flex flex-col justify-center max-w-175">
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
        <div className="flex flex-col w-100 mx-auto md:mx-0 md:max-w-none justify-center pt-10 font-sans">
          <img src="full_logo.png" className="pb-5 w-50 mx-auto"/>
          <h2 className="text-blue-900 text-2xl font-semibold">Welcome Back</h2>
          <p className="mb-6 text-blue-900">
            Enter your credentials to access your account
          </p>
          <input className="input validator bg-white border-black text-black mb-3 w-full" type="email" required placeholder="Email" />
          <input className="input bg-white border-black text-black mb-3 w-full" type="password" required placeholder="Password" />
          <p className="text-right text-blue-900">Forgot Password?</p>
          {/* Signin Button */}
          <button
            //onClick={}
            className="w-full px-3 py-5 my-3 bg-[#4285F4] text-white border-none rounded-sm text-4 font-medium flex items-center justify-center gap-3 hover:bg-[#357ae8]"
          >
            Sign In
          </button>
          <p className="text-blue-900">Don't have an account? <Link to="/signup">Create an account</Link></p>
        </div>
      </div>
    </div>
  );
}
