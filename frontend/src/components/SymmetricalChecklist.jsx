import { useTheme } from "../context/ThemeContext";
import { Check } from "lucide-react";

export default function SymmetricalChecklist({ heading, items, className }) {
    const { theme } = useTheme();
    return (
        <div className={`rounded-xl border border-gray-100 dark:border-gray-800 p-5 ${className}`} style={{ background: theme.bg }}>
            {heading ?
                (<p className="text-xl font-medium uppercase text-center text-gray-400 mb-4 dark:text-gray-500">{heading}</p>) : null}
            <div className="flex flex-wrap justify-center gap-2.5">
                {items.map((item) => (
                    <div
                        key={item}
                        className="flex items-center gap-2 text-lg text-gray-800 dark:text-gray-200 flex-1 sm:min-w-[35%] min-w-[70%]"
                    >
                        <span className="flex h-4.5 w-4.5 shrink-0 items-center justify-center rounded-full bg-green-50 dark:bg-blue-950">
                            < Check className="h-2.5 w-2.5 stroke-blue-600 dark:stroke-blue-400" strokeWidth={2.5} />
                        </span>
                        {item}
                    </div>
                ))}
            </div>
        </div>
    );
}