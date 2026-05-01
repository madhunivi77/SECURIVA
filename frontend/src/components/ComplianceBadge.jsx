export default function ComplianceBadge({ icon: Icon, label, description }) {
  return (
    <div className="flex flex-col items-center text-center bg-gray-800 border border-gray-700 rounded-xl px-6 py-5 shadow-sm flex-1 min-w-[200px]">
      <div className="bg-blue-900 text-white rounded-full p-3 mb-3">
        <Icon className="h-5 w-5" />
      </div>
      <p className="font-semibold text-white text-xl mb-1">{label}</p>
      <p className="text-gray-400 text-lg font-light">{description}</p>
    </div>
  );
}