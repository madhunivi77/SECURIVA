export default function CapabilityCard({ className = "", icon: Icon, label, description, content }) {
    return (
        <div className={`rounded-xl border p-4 transition-colors  border-gray-800 bg-gray-900 hover:border-gray-700 flex-1 ${className}`}>
            <div className="flex items-start gap-3.5">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-950">
                    <Icon className="h-4 w-4 stroke-blue-400" strokeWidth={1.5} />
                </div>
                <div className="flex flex-col flex-1">
                    <div>
                        <p className="text-xl font-medium mb-0.5 text-white">{label}</p>
                        <p className="text-lg leading-relaxed text-gray-400">{description}</p>
                    </div>
                    {content}
                </div>
            </div>
        </div>
    );
}