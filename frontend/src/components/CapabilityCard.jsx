export default function CapabilityCard({ className = "", icon: Icon, label, description, content }) {
    return (
        <div className={`rounded-xl border border-gray-100 bg-gray-50 p-4 transition-colors hover:border-gray-200 dark:border-gray-800 dark:bg-gray-900 dark:hover:border-gray-700 flex-1 ${className}`}>
            <div className="flex items-start gap-3.5">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-50 dark:bg-blue-950">
                    <Icon className="h-4 w-4 stroke-blue-600 dark:stroke-blue-400" strokeWidth={1.5} />
                </div>
                <div className="flex flex-col flex-1">
                    <div>
                        <p className="text-xl font-medium text-gray-900 mb-0.5 dark:text-white">{label}</p>
                        <p className="text-lg text-gray-500 leading-relaxed dark:text-gray-400">{description}</p>
                    </div>
                    {content}
                </div>
            </div>
        </div>
    );
}