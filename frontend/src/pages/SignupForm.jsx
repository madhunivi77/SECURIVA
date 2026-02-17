import { useState } from "react";
import { Link, useOutletContext } from "react-router-dom";

export default function SignupForm() {

  const {onGoogleLogin, onSalesforceLogin, isAuthenticated = false} = useOutletContext();

  const [loadingGoogle, setLoadingGoogle] = useState(false);
  const [loadingSalesforce, setLoadingSalesforce] = useState(false);

  const handleGoogleLogin = () => {
    setLoadingGoogle(true);
    if (onGoogleLogin) {
      onGoogleLogin();
    } else {
      window.location.href = "http://localhost:8000/login";
    }
  };

  const handleSalesforceLogin = () => {
    setLoadingSalesforce(true);
    if (onSalesforceLogin) {
      onSalesforceLogin();
    } else {
      window.location.href = "http://localhost:8000/salesforce/login";
    }
  };

  return (
    <div className="flex flex-col-reverse md:flex-row justify-center gap-5 text-center section-min-height bg-white">
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
      <form className="flex flex-col w-100 mx-auto md:mx-0 md:max-w-none justify-center pt-10 font-sans">
        <img src="full_logo.png" className="pb-5 w-50 mx-auto"/>
        <h2 className="text-blue-900 text-2xl font-semibold">Create your account</h2>
        <p className="mb-6 text-blue-900">
          Fill in your details to get started with Securiva.
        </p>
        <input id="email" className="input validator bg-white border-black text-black mb-3 w-full" type="email" required placeholder="Email" />
        <input id="phone" type="tel" className="input validator tabular-nums bg-white border-black text-black mb-3 w-full" required placeholder="Phone" 
          pattern="[0-9]*" minLength="10" maxLength="10" title="Must be 10 digits" />
        <input id="password" className="input bg-white border-black text-black mb-3 w-full" type="password" required placeholder="Password" minLength="8" 
          pattern="(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}" 
          title="Must be more than 8 characters, including number, lowercase letter, uppercase letter"/>
        <input className="input bg-white border-black text-black mb-3 w-full" type="password" required placeholder="Password" />
        <p className="text-blue-900"><input id="tos" type="checkbox" className="checkbox checkbox-info" required/> I agree to the Terms of Service and Privacy Policy</p>
        {/* Signin Button */}
        <button
          //onClick={}
          className="w-full px-3 py-5 my-3 bg-[#4285F4] text-white border-none rounded-sm text-4 font-medium flex items-center justify-center gap-3 hover:bg-[#357ae8]"
          style={{
            cursor: loadingGoogle ? "default" : "pointer",
            transition: "background-color 0.2s",
            opacity: loadingGoogle ? 0.7 : 1,
          }}
          type="submit"
        >
          Create account
        </button>
        <p className="text-blue-900">Already have an account? <Link to="/login">Sign In</Link></p>
      </form>
    </div>
  );
}

/* ----------------- Styles ------------------- */

const inputStyle = {
  width: "100%",
  padding: "10px",
  marginBottom: "12px",
  borderRadius: "6px",
  border: "1px solid #555",
  backgroundColor: "#1e1e1e",
  color: "white",
  boxSizing: "border-box",
};

const buttonStyle = (backgroundColor, width = "100%") => ({
  width,
  padding: "10px",
  backgroundColor,
  color: "white",
  border: "none",
  borderRadius: "6px",
  cursor: "pointer",
});
