import { useState } from "react";
import { useTranslation } from "react-i18next";

export default function Support() {
  const { t } = useTranslation();

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    category: "Technical Issue",
    message: "",
  });

  const handleChange = (e) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    alert(t("support.form.success"));
    setFormData({
      name: "",
      email: "",
      category: "Technical Issue",
      message: "",
    });
  };

  return (
    <div className="bg-[#0a0f1f] text-white">

      {/* HERO */}
      <section className="hero py-24 bg-linear-to-br from-blue-900 to-black text-white">
        <div className="hero-content text-center max-w-4xl">
          <div>
            <h1 className="text-5xl font-bold mb-6">
              {t("support.hero.title")}
            </h1>
            <p className="text-xl opacity-90">
              {t("support.hero.subtitle")}
            </p>
          </div>
        </div>
      </section>

      {/* SUPPORT AREAS */}
      <section className="px-5 lg:px-20 pt-12 pb-20">
        <h2 className="text-4xl font-mono text-center mb-12">
          {t("support.sections.supportAreasTitle")}
        </h2>

        <div className="grid md:grid-cols-3 gap-10">

          {/* ACCOUNT */}
          <div className="card bg-[#111633] shadow-xl">
            <div className="card-body">
              <h3 className="card-title text-xl">
                {t("support.supportAreas.account.title")}
              </h3>

              <p className="text-blue-200">
                {t("support.supportAreas.account.description")}
              </p>

              <div className="text-sm opacity-80 mt-3">
                <p className="font-semibold">
                  {t("support.supportAreas.account.commonTitle")}
                </p>
                <ul className="list-disc ml-6 mt-2 space-y-1">
                  {t("support.supportAreas.account.items", { returnObjects: true }).map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* PLATFORM */}
          <div className="card bg-[#111633] shadow-xl">
            <div className="card-body">
              <h3 className="card-title text-xl">
                {t("support.supportAreas.platform.title")}
              </h3>

              <p className="text-blue-200">
                {t("support.supportAreas.platform.description")}
              </p>

              <div className="text-sm opacity-80 mt-3">
                <p className="font-semibold">
                  {t("support.supportAreas.platform.commonTitle")}
                </p>
                <ul className="list-disc ml-6 mt-2 space-y-1">
                  {t("support.supportAreas.platform.items", { returnObjects: true }).map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* SECURITY */}
          <div className="card bg-[#111633] shadow-xl">
            <div className="card-body">
              <h3 className="card-title text-xl">
                {t("support.supportAreas.security.title")}
              </h3>

              <p className="text-blue-200">
                {t("support.supportAreas.security.description")}
              </p>

              <div className="text-sm opacity-80 mt-3">
                <p className="font-semibold">
                  {t("support.supportAreas.security.commonTitle")}
                </p>
                <ul className="list-disc ml-6 mt-2 space-y-1">
                  {t("support.supportAreas.security.items", { returnObjects: true }).map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* PROCESS */}
      <section className="px-20 pb-20">
        <h2 className="text-3xl font-mono text-center mb-8">
          {t("support.sections.processTitle")}
        </h2>

        <div className="grid md:grid-cols-4 gap-8 text-center">
          {t("support.process.steps", { returnObjects: true }).map((step, i) => (
            <div key={i}>
              <div className="text-4xl font-bold text-blue-400 mb-2">
                {i + 1}
              </div>
              <p className="font-semibold">{step.title}</p>
              <p className="text-sm text-blue-200 mt-2">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* FAQ */}
      <section className="px-5 lg:px-20 pb-20">
        <h2 className="text-4xl font-mono text-center mb-12">
          {t("support.sections.faqTitle")}
        </h2>

        <div className="max-w-4xl mx-auto space-y-4">

          {["q1", "q2", "q3", "q4"].map((q) => (
            <div key={q} className="collapse collapse-arrow bg-[#111633]">
              <input type="checkbox" />
              <div className="collapse-title text-lg font-medium">
                {t(`support.faq.${q}.question`)}
              </div>
              <div className="collapse-content text-blue-200">
                {t(`support.faq.${q}.answer`)}
              </div>
            </div>
          ))}

        </div>
      </section>

      {/* FORM */}
      <section className="px-5 lg:px-20 pb-20">
        <div className="max-w-3xl mx-auto bg-[#111633] p-10 rounded-2xl shadow-xl">

          <h2 className="text-3xl font-mono mb-6 text-center">
            {t("support.sections.formTitle")}
          </h2>

          <form onSubmit={handleSubmit} className="space-y-6">

            <input
              name="name"
              className="input input-bordered w-full"
              placeholder={t("support.form.name")}
              value={formData.name}
              onChange={handleChange}
              required
            />

            <input
              name="email"
              className="input input-bordered w-full"
              placeholder={t("support.form.email")}
              value={formData.email}
              onChange={handleChange}
              required
            />

            <select
              name="category"
              className="select select-bordered w-full"
              value={formData.category}
              onChange={handleChange}
            >
              {t("support.form.categoryOptions", { returnObjects: true }).map((opt, i) => (
                <option key={i}>{opt}</option>
              ))}
            </select>

            <textarea
              name="message"
              className="textarea textarea-bordered w-full h-40"
              placeholder={t("support.form.message")}
              value={formData.message}
              onChange={handleChange}
              required
            />

            <button className="btn btn-primary w-full text-lg">
              {t("support.form.button")}
            </button>

          </form>
        </div>
      </section>

      {/* COMMITMENT */}
      <section className="px-5 lg:px-20 pb-24 text-center">
        <h2 className="text-3xl font-mono mb-4">
          {t("support.sections.commitmentTitle")}
        </h2>

        <p className="text-blue-200 text-lg max-w-3xl mx-auto">
          {t("support.sections.commitmentText")}
        </p>

        <div className="mt-8 flex justify-center gap-6 flex-wrap">
          {t("support.badges", { returnObjects: true }).map((b, i) => (
            <div key={i} className="badge badge-lg badge-outline">
              {b}
            </div>
          ))}
        </div>
      </section>

    </div>
  );
}