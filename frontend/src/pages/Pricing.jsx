import { Check } from "lucide-react";

function Feature({ children }) {
  return (
    <div className="flex gap-3 items-start">
      <Check size={18} className="mt-1 shrink-0 text-primary" />
      <span>{children}</span>
    </div>
  );
}

export default function Pricing() {

  return (
    <div className="min-h-screen flex flex-col gap-8 items-center py-24 px-4">

      {/* Title */}
      <div className="flex flex-col gap-2 text-center">
        <h1 className="font-bold text-3xl">Pricing</h1>
        <span className="text-base-content/70">
          Whatever your status, our offers evolve according to your needs
        </span>
      </div>

      {/* Pricing cards */}
      <div className="flex flex-col md:flex-row gap-8 px-2 max-w-6xl w-full items-center md:items-stretch justify-center">

        {/* Basic */}
        <div className="flex flex-col gap-6 bg-[#091932] rounded-box p-8 flex-1 max-w-sm">
          <div className="flex flex-col gap-4 text-center pt-13">
            <h2 className="text-xl">Starter</h2>

            <h1 className="text-5xl font-bold">$29/month</h1>

            <span className="text-sm">Best for entrepreneurs and small businesses</span>
          </div>

          <div className="flex flex-col gap-2 flex-1">
            <Feature> Task automation & email scheduling</Feature>
            <Feature>AI chat assistant (text-based)</Feature>
            <Feature>Basic reports & analytics</Feature>
            <Feature>Up to 3 platform integrations</Feature>
            <Feature>Standard support</Feature>
          </div>

          <button className="btn btn-neutral">Sign up</button>
        </div>

        {/* Startup (Most popular) */}
        <div className="flex flex-col gap-6 bg-[#091932] rounded-box p-8 border border-primary shadow flex-1 max-w-sm">

          <div className="badge badge-primary self-center badge-lg">
            Most popular
          </div>

          <div className="flex flex-col gap-4 text-center">
            <h2 className="text-xl">Professional</h2>

            <h1 className="text-5xl font-bold">
              $89/month
            </h1>

            <span className="text-sm">
              Ideal for growing businesses
            </span>
          </div>

          <div className="flex flex-col gap-2 flex-1">
            <Feature>All Basic features</Feature>
            <Feature>AI-powered cybersecurity protection</Feature>
            <Feature>Voice & video assistant interactions</Feature>
            <Feature>eBook and document generation</Feature>
            <Feature>Up to 10 integrations</Feature>
            <Feature>24/7 priority support</Feature>
          </div>

          <button className="btn btn-primary">Sign up</button>
        </div>

        {/* Team */}
        <div className="flex flex-col gap-6 bg-[#091932] rounded-box p-8 flex-1 max-w-sm">
          <div className="flex flex-col gap-4 text-center pt-13">
            <h2 className="text-xl">Enterprise</h2>

            <h1 className="text-5xl font-bold">
              Custom
            </h1>

            <span className="text-sm">
              For large-scale organizations
            </span>
          </div>

          <div className="flex flex-col gap-2 flex-1">
            <Feature> Full automation suite + AI-managed VPN</Feature>
            <Feature> Digital Twin business simulation</Feature>
            <Feature> Multi-language AI avatar assistant</Feature>
            <Feature> Unlimited integrations and API access</Feature>
            <Feature> Dedicated account manager</Feature>
            <Feature> SLA-guaranteed uptime and compliance (GDPR/HIPAA-ready)</Feature>
          </div>

          <button className="btn btn-neutral">Sign up</button>
        </div>

      </div>
    </div>
  );
}
