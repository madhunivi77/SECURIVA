import { Link, useNavigate } from "react-router-dom";
import { ChevronLeft } from "lucide-react";
import Copyright from "../components/Copyright";

export default function LoginForm() {
  const navigate = useNavigate();

  return (
    <div className="bg-[#000020] w-screen min-h-screen flex flex-col relative">

      {/* Back Button */}
      <button
        onClick={() => navigate(-1)}
        className="text-white absolute top-4 left-4 z-10"
      >
        <ChevronLeft size={32} />
      </button>

      {/* Center Section */}
      <div className="flex-1 flex flex-col justify-center">
        <div className="flex flex-col-reverse md:flex-row justify-center items-center gap-10 text-center px-6">

          {/* Video Section */}
          <div className="flex flex-col justify-center w-auto md:w-[40%]">
            <video
              autoPlay
              loop
              muted
              playsInline
              className="w-full rounded-lg"
            >
              <source
                src="/landing_page/SecurivaHero.mp4"
                type="video/mp4"
              />
              Your browser does not support the video tag.
            </video>
          </div>

          {/* Login Form Section */}
          <div className="flex flex-col w-full max-w-md justify-center font-sans">
            <img
              src="LOGO_FOOTER_0000.png"
              className="pb-5 w-40 mx-auto"
              alt="Logo"
            />

            <h2 className="text-2xl font-semibold text-white">
              Welcome Back
            </h2>

            <p className="mb-6 text-gray-300">
              Enter your credentials to access your account
            </p>

            <input
              className="input bg-slate-800 border-black text-white mb-3 w-full"
              type="email"
              required
              placeholder="Email"
            />

            <input
              className="input bg-slate-800 border-black text-white mb-3 w-full"
              type="password"
              required
              placeholder="Password"
            />

            <p className="text-right text-sm text-gray-400 hover:text-white cursor-pointer">
              Forgot Password?
            </p>

            <button
              className="w-full px-3 py-4 my-4 bg-[#4285F4] text-white rounded-sm font-medium flex items-center justify-center gap-3 hover:bg-[#357ae8] transition-colors"
            >
              Sign In
            </button>

            <p className="text-gray-300">
              Don't have an account?{" "}
              <Link to="/signup" className="text-blue-400 hover:text-blue-300">
                Create an account
              </Link>
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <Copyright />
    </div>
  );
}