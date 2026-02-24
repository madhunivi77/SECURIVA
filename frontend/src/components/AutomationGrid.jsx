import AutomationCard from "./AutomationCard";

const AutomationGrid = ({data = []}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {data.map((automation, index) => (
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