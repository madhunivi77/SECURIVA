import { ChevronRight } from "lucide-react";

export default function BulletList({ items }) {
  return (
    <ul className="mx-[15%] mb-6 grid sm:grid-cols-2 gap-x-8 gap-y-2">
      {items.map((item) => (
        <li key={item} className="flex items-start gap-2 text-gray-700 dark:text-gray-300 text-lg">
          <ChevronRight className="h-4 w-4 mt-0.5 text-blue-900 dark:text-blue-400 shrink-0" />
          {item}
        </li>
      ))}
    </ul>
  );
}