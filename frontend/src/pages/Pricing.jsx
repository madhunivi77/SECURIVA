import { useState } from "react";

export default function Pricing() {
  const [annual, setAnnual] = useState(false);

  return (
    <div className="min-h-screen flex flex-col gap-8 items-center pt-24 px-4">

      {/* Title */}
      <div className="flex flex-col gap-2 text-center">
        <h1 className="font-bold text-3xl">Pricing</h1>
        <span className="text-base-content/70">
          Whatever your status, our offers evolve according to your needs
        </span>
      </div>

      {/* Monthly / Annual Toggle */}
      <div className="flex gap-2 items-center">
        <span>Monthly</span>

        <input
          type="checkbox"
          className="toggle toggle-primary"
          checked={annual}
          onChange={(e) => setAnnual(e.target.checked)}
        />

        <span className="flex flex-col">
          Annual
          <span className="text-sm text-accent">(Save up to 10%)</span>
        </span>
      </div>

      {/* Pricing cards */}
      <div className="flex gap-8 px-2 max-w-6xl w-full justify-center">

        {/* Free */}
        <div className="flex flex-col gap-6 bg-[#091932] rounded-box p-8 flex-1 max-w-sm">
          <div className="flex flex-col gap-4 text-center pt-13">
            <h2 className="text-xl">Free</h2>

            <h1 className="text-5xl font-bold">Free</h1>

            <span className="text-sm">Free forever</span>
          </div>

          <div className="flex flex-col gap-2">
            <div className="flex gap-2 items-center">✅ 1 user</div>
            <div className="flex gap-2 items-center">✅ Plan features</div>
            <div className="flex gap-2 items-center">✅ Product support</div>
          </div>

          <button className="btn btn-neutral">Sign up</button>
        </div>

        {/* Startup (Most popular) */}
        <div className="flex flex-col gap-6 bg-[#091932] rounded-box p-8 border border-primary shadow flex-1 max-w-sm">

          <div className="badge badge-primary self-center badge-lg">
            Most popular
          </div>

          <div className="flex flex-col gap-4 text-center">
            <h2 className="text-xl">Startup</h2>

            <h1 className="text-5xl font-bold">
              ${annual ? "35" : "39"}
            </h1>

            <span className="text-sm">
              All the basics for starting a new business
            </span>
          </div>

          <div className="flex flex-col gap-2">
            <div className="flex gap-2 items-center">✅ 2 users</div>
            <div className="flex gap-2 items-center">✅ Plan features</div>
            <div className="flex gap-2 items-center">✅ Product support</div>
          </div>

          <button className="btn btn-primary">Sign up</button>
        </div>

        {/* Team */}
        <div className="flex flex-col gap-6 bg-[#091932] rounded-box p-8 flex-1 max-w-sm">
          <div className="flex flex-col gap-4 text-center pt-13">
            <h2 className="text-xl">Team</h2>

            <h1 className="text-5xl font-bold">
              ${annual ? "80" : "89"}
            </h1>

            <span className="text-sm">
              Everything you need for a growing business
            </span>
          </div>

          <div className="flex flex-col gap-2">
            <div className="flex gap-2 items-center">✅ 10 users</div>
            <div className="flex gap-2 items-center">✅ Plan features</div>
            <div className="flex gap-2 items-center">✅ Product support</div>
          </div>

          <button className="btn btn-neutral">Sign up</button>
        </div>

      </div>
    </div>
  );
}
