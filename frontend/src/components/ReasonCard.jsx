import { useTheme } from "../context/ThemeContext";

export default function ReasonCard({ icon: Icon, label, description }){
    const {theme} = useTheme();
    return (
        <div className={`flex flex-col gap-3 rounded-2xl border p-5 transition-colors border-gray-800 bg-[${theme.bg}] hover:border-gray-700 flex-1 min-w-80 max-w-1/3`}>
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-blue-950">
            <Icon className="h-4 w-4 stroke-blue-400" strokeWidth={1.5} />
            </div>
            <div>
            <p className="text-xl font-medium mb-1 text-white">{label}</p>
            <p className="text-lg leading-relaxed text-gray-400">{description}</p>
            </div>
        </div>
    );
};