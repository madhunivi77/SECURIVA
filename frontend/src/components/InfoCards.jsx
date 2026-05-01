import InfoCard from "./InfoCard";

export default function InfoCards({ cards }) {
  return (
    <div className="flex flex-wrap gap-3 mb-6 mx-[15%]">
      {cards.map((card) => (
        <InfoCard key={card.label} {...card} />
      ))}
    </div>
  );
}