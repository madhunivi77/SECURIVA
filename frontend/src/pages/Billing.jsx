import { useEffect, useState } from "react";
import { CreditCard, CheckCircle, Loader2, AlertCircle, ExternalLink } from "lucide-react";

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

export default function Billing() {
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

  return (
    <div className="p-6 max-w-5xl mx-auto" style={{ fontFamily: MONO }}>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1
            className="text-xl font-semibold tracking-tight mb-1"
            style={{ color: "var(--ink)" }}
          >
            Billing & Plans
          </h1>
          <p className="text-[13px]" style={{ color: "var(--ink-muted)" }}>
            Manage your subscription and payment details.
          </p>
        </div>
        <button
          onClick={handlePortal}
          disabled={portalLoading || loading || !subscriptionStatus?.subscription_id}
          className="flex items-center gap-2 px-3 py-1.5 rounded-md text-[12px] font-medium transition-colors"
          style={{
            background: "var(--bg-elev)",
            border: "1px solid var(--ivory-3)",
            color: "var(--ink)",
          }}
        >
          {portalLoading ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <ExternalLink className="w-3.5 h-3.5" />
          )}
          Manage subscription
        </button>
      </div>

      {/* Error banner */}
      {error && (
        <div
          className="flex items-center gap-2 px-4 py-3 rounded-md mb-6 text-[12px]"
          style={{ background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.25)", color: "#ef4444" }}
        >
          <AlertCircle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {/* past_due warning */}
      {activeStatus === "past_due" && (
        <div
          className="flex items-center gap-2 px-4 py-3 rounded-md mb-6 text-[12px]"
          style={{ background: "rgba(234,179,8,0.08)", border: "1px solid rgba(234,179,8,0.35)", color: "#ca8a04" }}
        >
          <AlertCircle className="w-4 h-4 shrink-0" />
          Your last payment failed. Please{" "}
          <button
            onClick={handlePortal}
            className="underline font-medium ml-1"
            style={{ color: "#ca8a04", background: "none", border: "none", cursor: "pointer" }}
          >
            update your billing info
          </button>{" "}
          to restore Pro access.
        </div>
      )}

      {/* Stripe not configured notice */}
      {!loading && !config && !error && (
        <div
          className="flex items-center gap-2 px-4 py-3 rounded-md mb-6 text-[12px]"
          style={{ background: "var(--bg-elev)", border: "1px solid var(--ivory-3)", color: "var(--ink-muted)" }}
        >
          <CreditCard className="w-4 h-4 shrink-0" />
          Stripe is not configured. Set <code className="mx-1 px-1 rounded" style={{ background: "var(--ivory-2)" }}>STRIPE_SECRET_KEY</code> in your environment to enable billing.
        </div>
      )}

      {/* Plans */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {PLANS.map((plan) => (
          <div
            key={plan.name}
            className="flex flex-col rounded-lg p-5 transition-all"
            style={{
              background: plan.highlight ? "var(--securiva-red)" : "var(--bg-elev)",
              border: plan.highlight
                ? "1px solid var(--securiva-red)"
                : "1px solid var(--ivory-3)",
              color: plan.highlight ? "#fff" : "var(--ink)",
            }}
          >
            <div className="mb-4">
              <p
                className="text-[11px] uppercase tracking-[0.1em] font-semibold mb-1"
                style={{ color: plan.highlight ? "rgba(255,255,255,0.7)" : "var(--ink-soft)" }}
              >
                {plan.name}
              </p>
              <div className="flex items-baseline gap-1">
                <span className="text-3xl font-bold">{plan.price}</span>
                {plan.period && (
                  <span
                    className="text-[12px]"
                    style={{ color: plan.highlight ? "rgba(255,255,255,0.6)" : "var(--ink-muted)" }}
                  >
                    {plan.period}
                  </span>
                )}
              </div>
              <p
                className="text-[12px] mt-1.5"
                style={{ color: plan.highlight ? "rgba(255,255,255,0.7)" : "var(--ink-muted)" }}
              >
                {plan.description}
              </p>
            </div>

            <ul className="flex-1 space-y-2 mb-5">
              {plan.features.map((f) => (
                <li key={f} className="flex items-start gap-2 text-[12px]">
                  <CheckCircle
                    className="w-3.5 h-3.5 mt-0.5 shrink-0"
                    style={{ color: plan.highlight ? "rgba(255,255,255,0.8)" : "var(--securiva-red)" }}
                  />
                  <span style={{ color: plan.highlight ? "rgba(255,255,255,0.85)" : "var(--ink-soft)" }}>
                    {f}
                  </span>
                </li>
              ))}
            </ul>

            {plan.name === activePlanName ? (
              <div
                className="text-center text-[12px] py-2 rounded-md font-medium"
                style={{
                  background: plan.highlight ? "rgba(255,255,255,0.15)" : "var(--ivory-2)",
                  color: plan.highlight ? "#fff" : "var(--ink-muted)",
                }}
              >
                Current plan
              </div>
            ) : plan.priceId === "enterprise" ? (
              <a
                href="mailto:sales@securiva.io"
                className="block text-center text-[12px] py-2 rounded-md font-medium transition-opacity hover:opacity-80"
                style={{
                  background: plan.highlight ? "#fff" : "var(--ink)",
                  color: plan.highlight ? "var(--securiva-red)" : "#fff",
                }}
              >
                Contact sales
              </a>
            ) : plan.priceId !== null ? (
              <button
                onClick={() => handleCheckout(plan)}
                disabled={checkoutLoading === plan.name || !config}
                className="flex items-center justify-center gap-2 text-[12px] py-2 rounded-md font-medium transition-opacity hover:opacity-80 disabled:opacity-50"
                style={{
                  background: plan.highlight ? "#fff" : "var(--ink)",
                  color: plan.highlight ? "var(--securiva-red)" : "#fff",
                }}
              >
                {checkoutLoading === plan.name ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : null}
                {checkoutLoading === plan.name ? "Redirecting…" : "Upgrade"}
              </button>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}
