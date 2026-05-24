import {Zap} from "lucide-react";
import Checklist from "./Checklist";

export default function SolutionCard({ number, icon: Icon, label, description, content, points, footer, examples, isFuture, imageLink, altText }) {
    return (
        <div className="flex gap-6 rounded-2xl border p-6 transition-colors border-gray-800 bg-inherit hover:border-gray-700">

            {/* Number + icon */}
            <div className="flex flex-col items-center gap-3 pt-1">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-950">
                    <Icon className="h-5 w-5 stroke-blue-400" strokeWidth={1.5} />
                </div>
                <span className="text-lg font-medium tabular-nums text-gray-700">{number}</span>
            </div>
            <div className="flex sm:flex-row flex-col justify-between flex-1">
                {/* Content */}
                <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                        <h3 className="text-xl font-medium text-white">{label}</h3>
                        {isFuture && (
                            <span className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider border-purple-800 bg-purple-950 text-purple-400">
                                <Zap className="h-2.5 w-2.5 fill-purple-500 stroke-none" />
                                Coming Soon
                            </span>
                        )}
                    </div>
                    {description && (<p className="text-lg  mb-3 leading-relaxed text-gray-400">{description}</p>)}
                    {content}
                    {points && (<Checklist items={points} size={"3.5"} />)}
                    {examples && (
                        <div className="mt-3 flex flex-wrap gap-2">
                            {examples.map((ex) => (
                                <span key={ex} className="rounded-lg border px-3 py-1 text-[12px] italic border-gray-800 bg-gray-900 text-gray-400">
                                    "{ex}"
                                </span>
                            ))}
                        </div>
                    )}
                    {footer && (<p className="text-lg my-3 leading-relaxed text-gray-400">{footer}</p>)}
                </div>

                {imageLink && 
                    (
                        <figure>
                            <img
                                src={imageLink}
                                alt={altText}
                                className="w-50" />
                        </figure>
                    )
                }
            </div>

        </div>
    );
}
