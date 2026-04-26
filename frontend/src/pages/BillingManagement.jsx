import { useEffect, useState } from "react";
import { CreditCard, CheckCircle, Loader2, AlertCircle, ExternalLink, TrendingUp, Calendar, DollarSign } from "lucide-react";

const MONO = '"Geist Mono", ui-monospace, SFMono-Regular, "SF Mono", Menlo, monospace';

const PLANS = [
  {
    name: "Starter",
    price: "$0",
    period: "/ month",
    description: "For individuals and small teams getting started.",
    features: ["5,000 AI messages / mo", "Text & voice agent", "Basic compliance tools", "Community support"],
    priceId: null,
    highlight: false,
  },
  {
    name: "Pro",
    price: "$49",
    period: "/ month",
    description: "For growing teams that need more power.",
    features: ["50,000 AI messages / mo", "All MCP tools", "Full compliance suite", "TeleSign SMS & voice", "Priority support"],
    priceId: "pro",
    highlight: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    description: "For organizations with advanced needs.",
    features: ["Unlimited messages", "Dedicated infrastructure", "SSO / SAML", "Custom integrations", "SLA + dedicated support"],
    priceId: "enterprise",
    highlight: false,
  },
];

export default function BillingManagement() {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);
  const [checkoutLoading, setCheckoutLoading] = useState(null);
  const [portalLoading, setPortalLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      fetch("/stripe/config", { credentials: "include" }).then((r) => r.json()),
      fetch("/stripe/subscription/status", { credentials: "include" })
        .then((r) => r.json())
        .catch(() => null),
    ])
      .then(([configData, statusData]) => {
        if (configData.error) setError(configData.error);
        else setConfig(configData);
        if (statusData && !statusData.error) setSubscriptionStatus(statusData);
      })
      .catch(() => setError("Could not reach billing server."))
      .finally(() => setLoading(false));
  }, []);

  const handleCheckout = async (plan) => {
    if (!plan.priceId || plan.priceId === "enterprise") return;
    setCheckoutLoading(plan.name);
    setError(null);
    try {
      const res = await fetch("/stripe/checkout/session", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          price_id: config?.default_price_id || plan.priceId,
          mode: "subscription",
        }),
      });
      const data = await res.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        setError(data.error || "Checkout failed.");
      }
    } catch {
      setError("Checkout request failed.");
    } finally {
      setCheckoutLoading(null);
    }
  };

  const handlePortal = async () => {
    setPortalLoading(true);
    setError(null);
    try {
      const res = await fetch("/stripe/billing-portal/session", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ return_url: window.location.href }),
      });
      const data = await res.json();
      if (data.portal_url) {
        window.location.href = data.portal_url;
      } else {
        setError(data.error || "Could not open billing portal.");
      }
    } catch {
      setError("Billing portal request failed.");
    } finally {
      setPortalLoading(false);
    }
  };

  // Derive which plan is currently active
  const activeStatus = subscriptionStatus?.status;
  const activePlanName =
    activeStatus === "active" || activeStatus === "trialing" ? "Pro" : "Starter";

  // Calculate usage percentage
  const usagePercentage = subscriptionStatus
    ? Math.min((subscriptionStatus.messages_this_month / subscriptionStatus.quota) * 100, 100)
    : 0;

  return (
    <div className="p-6 h-full overflow-auto" style={{ fontFamily: MONO }}>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight mb-2 text-white">
          Billing & Subscription
        </h1>
        <p className="text-sm text-gray-400">
          Manage your subscription, view usage, and update payment details.
        </p>
      </div>

      {/* Error banner */}
      {error && (
        <div className="flex items-center gap-2 px-4 py-3 rounded-md mb-6 text-sm bg-red-500/10 border border-red-500/20 text-red-400">
          <AlertCircle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {/* past_due warning */}
      {activeStatus === "past_due" && (
        <div className="flex items-center gap-2 px-4 py-3 rounded-md mb-6 text-sm bg-yellow-500/10 border border-yellow-500/20 text-yellow-400">
          <AlertCircle className="w-4 h-4 shrink-0" />
          Your last payment failed. Please{" "}
          <button
            onClick={handlePortal}
            className="underline font-medium ml-1 hover:text-yellow-300"
          >
            update your billing info
          </button>{" "}
          to restore Pro access.
        </div>
      )}

      {/* Current Subscription Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {/* Current Plan */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <CreditCard className="w-4 h-4 text-blue-400" />
            <p className="text-xs uppercase tracking-wide text-gray-400">Current Plan</p>
          </div>
          <p className="text-2xl font-bold text-white">{activePlanName}</p>
          <p className="text-sm text-gray-400 mt-1">
            {activeStatus === "trialing" ? "Free trial active" : activeStatus === "active" ? "Active subscription" : "Free plan"}
          </p>
        </div>

        {/* Usage This Month */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-green-400" />
            <p className="text-xs uppercase tracking-wide text-gray-400">Usage This Month</p>
          </div>
          <p className="text-2xl font-bold text-white">
            {subscriptionStatus?.messages_this_month?.toLocaleString() || 0}
          </p>
          <p className="text-sm text-gray-400 mt-1">
            of {subscriptionStatus?.quota?.toLocaleString() || 0} messages
          </p>
          <div className="mt-3 w-full bg-gray-700 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all"
              style={{ width: `${usagePercentage}%` }}
            />
          </div>
        </div>

        {/* Next Billing */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <Calendar className="w-4 h-4 text-purple-400" />
            <p className="text-xs uppercase tracking-wide text-gray-400">Next Billing</p>
          </div>
          <p className="text-2xl font-bold text-white">
            {activeStatus === "active" || activeStatus === "trialing" ? "$49" : "$0"}
          </p>
          <p className="text-sm text-gray-400 mt-1">
            {activeStatus === "trialing" ? "After trial ends" : activeStatus === "active" ? "Monthly renewal" : "No billing"}
          </p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="flex gap-3 mb-8">
        <button
          onClick={handlePortal}
          disabled={portalLoading || loading || !subscriptionStatus?.subscription_id}
          className="flex items-center gap-2 px-4 py-2.5 rounded-md text-sm font-medium transition-colors bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {portalLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <ExternalLink className="w-4 h-4" />
          )}
          Manage Billing
        </button>
        {activePlanName === "Starter" && (
          <button
            onClick={() => handleCheckout(PLANS[1])}
            disabled={checkoutLoading === "Pro"}
            className="flex items-center gap-2 px-4 py-2.5 rounded-md text-sm font-medium transition-colors bg-gray-700 hover:bg-gray-600 text-white disabled:opacity-50"
          >
            {checkoutLoading === "Pro" ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <DollarSign className="w-4 h-4" />
            )}
            Upgrade to Pro
          </button>
        )}
      </div>

      {/* Plans Section */}
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-white mb-2">Available Plans</h2>
        <p className="text-sm text-gray-400 mb-6">
          Choose the plan that best fits your needs. Upgrade or downgrade anytime.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {PLANS.map((plan) => (
          <div
            key={plan.name}
            className={`flex flex-col rounded-lg p-6 transition-all ${
              plan.highlight
                ? "bg-blue-600 border border-blue-500"
                : "bg-gray-800 border border-gray-700"
            }`}
          >
            <div className="mb-4">
              <p className="text-xs uppercase tracking-wide font-semibold mb-1 text-gray-300">
                {plan.name}
              </p>
              <div className="flex items-baseline gap-1">
                <span className="text-3xl font-bold text-white">{plan.price}</span>
                {plan.period && (
                  <span className="text-sm text-gray-300">{plan.period}</span>
                )}
              </div>
              <p className="text-sm mt-2 text-gray-300">
                {plan.description}
              </p>
            </div>

            <ul className="flex-1 space-y-2 mb-5">
              {plan.features.map((f) => (
                <li key={f} className="flex items-start gap-2 text-sm">
                  <CheckCircle className="w-4 h-4 mt-0.5 shrink-0 text-green-400" />
                  <span className="text-gray-200">{f}</span>
                </li>
              ))}
            </ul>

            {plan.name === activePlanName ? (
              <div className="text-center text-sm py-2 rounded-md font-medium bg-gray-700 text-gray-300">
                Current plan
              </div>
            ) : plan.priceId === "enterprise" ? (
              <a
                href="mailto:sales@securiva.io"
                className="block text-center text-sm py-2 rounded-md font-medium transition-opacity hover:opacity-80 bg-white text-gray-900"
              >
                Contact sales
              </a>
            ) : plan.priceId !== null ? (
              <button
                onClick={() => handleCheckout(plan)}
                disabled={checkoutLoading === plan.name || !config}
                className="flex items-center justify-center gap-2 text-sm py-2 rounded-md font-medium transition-opacity hover:opacity-80 disabled:opacity-50 bg-white text-gray-900"
              >
                {checkoutLoading === plan.name ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : null}
                {checkoutLoading === plan.name ? "Redirecting…" : "Upgrade"}
              </button>
            ) : null}
          </div>
        ))}
      </div>

      {/* Stripe not configured notice */}
      {!loading && !config && !error && (
        <div className="flex items-center gap-2 px-4 py-3 rounded-md mt-6 text-sm bg-gray-800 border border-gray-700 text-gray-400">
          <CreditCard className="w-4 h-4 shrink-0" />
          Stripe is not configured. Set <code className="mx-1 px-1 rounded bg-gray-700">STRIPE_SECRET_KEY</code> in your environment to enable billing.
        </div>
      )}
    </div>
  );
}