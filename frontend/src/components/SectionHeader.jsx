export default function SectionHeader({ title, subtitle }) {
  return (
    <>
      <h2 className="text-4xl font-normal text-center mb-2 text-white">
        {title}
      </h2>
      {subtitle && (
        <p className="text-xl font-light mb-8 text-center text-gray-400 mx-[15%]">
          {subtitle}
        </p>
      )}
    </>
  );
}