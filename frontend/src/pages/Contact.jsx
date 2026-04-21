import { useState } from "react";
import { useTranslation } from "react-i18next";

export default function Contact() {
  const { t } = useTranslation();

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
    alert(t("contact.form.success"));
    setFormData({
      name: "",
      email: "",
      company: "",
      type: "general",
      message: "",
    });
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">

      {/* ---------- HERO ---------- */}
      <section className="hero pt-24 pb-40 bg-[#0a0f1f] text-white">
        <div className="hero-content text-center max-w-4xl">
          <div>
            <h1 className="text-5xl font-bold mb-6">
              {t("contact.hero.title")}
            </h1>
            <p className="text-xl opacity-90">
              {t("contact.hero.description")}
            </p>
          </div>
        </div>
      </section>

      {/* ---------- CONTACT SERVICES ---------- */}
      <section className="relative overflow-hidden">
        <div className="relative w-full min-h-screen overflow-hidden bg-black mx-auto">

          <video
            autoPlay
            loop
            muted
            playsInline
            className="absolute top-0 left-0 w-full h-full object-cover opacity-50"
          >
            <source src="Video_1.mp4" type="video/mp4" />
          </video>

          <div className="absolute top-0 left-0 w-full h-64 bg-gradient-to-b from-[#0a0f1f] via-[#0a0f1f]/60 to-transparent pointer-events-none" />
          <div className="absolute bottom-0 left-0 w-full h-64 bg-gradient-to-t from-black via-gray-black/60 to-transparent pointer-events-none" />

          <div className="relative max-w-6xl mx-auto pt-50">

            <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">
              {t("contact.services.title")}
            </h2>

            <div className="grid md:grid-cols-3 gap-8">

              {/* SALES */}
              <div className="card bg-white/90 backdrop-blur dark:bg-gray-800/90 shadow-lg">
                <div className="card-body">
                  <h3 className="card-title">
                    {t("contact.services.sales.title")}
                  </h3>

                  <p>
                    {t("contact.services.sales.description")}
                  </p>

                  <div className="mt-4 text-sm opacity-80 space-y-1">
                    {t("contact.services.sales.items", { returnObjects: true }).map((item) => (
                      <p key={item}>• {item}</p>
                    ))}
                  </div>
                </div>
              </div>

              {/* SUPPORT */}
              <div className="card bg-white/90 backdrop-blur dark:bg-gray-800/90 shadow-lg">
                <div className="card-body">
                  <h3 className="card-title">
                    {t("contact.services.support.title")}
                  </h3>

                  <p>
                    {t("contact.services.support.description")}
                  </p>

                  <div className="mt-4 text-sm opacity-80 space-y-1">
                    {t("contact.services.support.items", { returnObjects: true }).map((item) => (
                      <p key={item}>• {item}</p>
                    ))}
                  </div>
                </div>
              </div>

              {/* PARTNERSHIP */}
              <div className="card bg-white/90 backdrop-blur dark:bg-gray-800/90 shadow-lg">
                <div className="card-body">
                  <h3 className="card-title">
                    {t("contact.services.partnership.title")}
                  </h3>

                  <p>
                    {t("contact.services.partnership.description")}
                  </p>

                  <div className="mt-4 text-sm opacity-80 space-y-1">
                    {t("contact.services.partnership.items", { returnObjects: true }).map((item) => (
                      <p key={item}>• {item}</p>
                    ))}
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>
      </section>

      {/* ---------- FORM ---------- */}
      <section className="py-20 px-10 bg-white dark:bg-black">
        <div className="max-w-4xl mx-auto">

          <h2 className="text-3xl font-bold text-center mb-4">
            {t("contact.form.title")}
          </h2>

          <p className="text-center opacity-80 mb-10">
            {t("contact.form.description")}
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">

            <div className="grid md:grid-cols-2 gap-6">

              <input
                name="name"
                value={formData.name}
                onChange={handleChange}
                type="text"
                placeholder={t("contact.form.fields.name")}
                className="input input-bordered w-full"
                required
              />

              <input
                name="email"
                value={formData.email}
                onChange={handleChange}
                type="email"
                placeholder={t("contact.form.fields.email")}
                className="input input-bordered w-full"
                required
              />
            </div>

            <input
              name="company"
              value={formData.company}
              onChange={handleChange}
              type="text"
              placeholder={t("contact.form.fields.company")}
              className="input input-bordered w-full"
            />

            <select
              name="type"
              value={formData.type}
              onChange={handleChange}
              className="select select-bordered w-full"
            >
              <option value="general">
                {t("contact.form.fields.type.general")}
              </option>
              <option value="sales">
                {t("contact.form.fields.type.sales")}
              </option>
              <option value="support">
                {t("contact.form.fields.type.support")}
              </option>
              <option value="partnership">
                {t("contact.form.fields.type.partnership")}
              </option>
            </select>

            <textarea
              name="message"
              value={formData.message}
              onChange={handleChange}
              className="textarea textarea-bordered w-full"
              rows={6}
              placeholder={t("contact.form.fields.message")}
              required
            />

            <button className="btn btn-primary w-full">
              {t("contact.form.button")}
            </button>

          </form>
        </div>
      </section>

      {/* ---------- POLICY ---------- */}
      <section className="py-20 px-10">
        <div className="max-w-6xl mx-auto">

          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">
            {t("contact.policy.title")}
          </h2>

          <div className="grid md:grid-cols-3 gap-8 text-center">

            {["responseTime", "availability", "global"].map((key) => (
              <div key={key} className="card bg-white dark:bg-gray-800 shadow-md">
                <div className="card-body">
                  <h3 className="font-bold text-lg">
                    {t(`contact.policy.${key}.title`)}
                  </h3>
                  <p className="text-3xl font-bold text-primary">
                    {t(`contact.policy.${key}.value`)}
                  </p>
                  <p className="opacity-80">
                    {t(`contact.policy.${key}.description`)}
                  </p>
                </div>
              </div>
            ))}

          </div>
        </div>
      </section>

      {/* ---------- COMPANY ---------- */}
      <section className="py-20 px-10 bg-white dark:bg-gray-800">
        <div className="max-w-5xl mx-auto text-center">

          <h2 className="text-3xl font-bold mb-8">
            {t("contact.company.title")}
          </h2>

          <div className="stats shadow">

            {["supportEmail", "hq", "security"].map((key) => (
              <div key={key} className="stat">
                <div className="stat-title">
                  {t(`contact.company.${key}.title`)}
                </div>
                <div className="stat-value text-lg">
                  {t(`contact.company.${key}.value`)}
                </div>
                <div className="stat-desc">
                  {t(`contact.company.${key}.description`)}
                </div>
              </div>
            ))}

          </div>
        </div>
      </section>

      {/* ---------- FAQ ---------- */}
      <section className="py-20 px-10">
        <div className="max-w-4xl mx-auto">

          <h2 className="text-3xl font-bold text-center mb-10">
            {t("contact.faq.title")}
          </h2>

          {["q1", "q2", "q3"].map((key) => (
            <div key={key} className="collapse collapse-arrow border bg-base-100 mb-4">
              <input type="checkbox" />

              <div className="collapse-title font-medium">
                {t(`contact.faq.${key}.question`)}
              </div>

              <div className="collapse-content">
                {t(`contact.faq.${key}.answer`)}
              </div>
            </div>
          ))}

        </div>
      </section>

    </div>
  );
}