import { useTheme } from "../context/ThemeContext";

export default function ReasonCard({ icon: Icon, label, description }){
    const {theme} = useTheme();
    return (
        <div className={`flex flex-col gap-3 rounded-2xl border border-gray-100 p-5 hover:border-gray-200 transition-colors dark:border-gray-800 bg-[${theme.bg}] dark:hover:border-gray-700 flex-1 min-w-80 max-w-1/3`}>
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-950">
            <Icon className="h-4 w-4 stroke-blue-600 dark:stroke-blue-400" strokeWidth={1.5} />
            </div>
            <div>
            <p className="text-lg font-medium text-gray-900 mb-1 dark:text-white">{label}</p>
            <p className="text-md text-gray-500 leading-relaxed dark:text-gray-400">{description}</p>
            </div>
        </div>
    );
};