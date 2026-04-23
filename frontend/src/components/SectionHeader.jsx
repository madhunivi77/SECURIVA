export default function SectionHeader({ title, subtitle }) {
  return (
    <>
      <h2 className="text-4xl font-normal text-center text-gray-900 mb-2 dark:text-white">
        {title}
      </h2>
      {subtitle && (
        <p className="text-xl font-light text-gray-500 mb-8 text-center dark:text-gray-400 mx-[15%]">
          {subtitle}
        </p>
      )}
    </>
  );
}