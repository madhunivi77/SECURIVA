import { CheckCircle2 } from "lucide-react";

export default function Checklist({className, items, size}) {
    return (
        <ul className="flex flex-col gap-1.5">
            {items.map((item) => (
                <li key={item} className={`flex items-start gap-2 text-lg text-gray-300 ${className}`}>
                    <CheckCircle2 className={`mt-2 h-${size} w-${size} shrink-0 stroke-blue-400" strokeWidth={2} `}/>
                    {item}
                </li>
            ))}
        </ul>
    );
}