import { useEffect } from "react";
import AutomationCard from "./AutomationCard";
import { useOutletContext } from "react-router-dom";

const AutomationGrid = () => {
  const {handleRefresh, cards:[cards]} = useOutletContext();
  console.log(cards);

  // refresh on initialization
  useEffect(() => {
    handleRefresh()
  }, []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {cards.map((automation, index) => (
        <AutomationCard
          key={automation.id}
          title={automation.title}
          description={automation.description}
          isActive={automation.isActive}
          lastRun={automation.lastRun}
          triggerCount={automation.triggerCount}
          index={index}
        />
      ))}
    </div>
  );
};

export default AutomationGrid;