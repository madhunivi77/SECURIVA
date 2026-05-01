export default function InfoCard({ icon: Icon, label, description }) {
  return (
    <div className="flex items-start gap-3 bg-gray-800 border border-gray-700 rounded-xl px-5 py-4 shadow-sm min-w-[260px] flex-1">
      <div className="mt-0.5 text-blue-400">
        <Icon className="h-5 w-5" strokeWidth={1.5} />
      </div>
      <div>
        <p className="text-xl font-medium text-white">{label}</p>
        <p className="text-lg text-gray-400 font-light mt-0.5">{description}</p>
      </div>
    </div>
  );
}