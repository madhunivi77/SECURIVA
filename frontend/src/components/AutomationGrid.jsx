import AutomationCard from "./AutomationCard";

const mockAutomations = [
  {
    id: 1,
    title: "Email Notification",
    description: "Send email when new lead is created",
    isActive: true,
    lastRun: "2 hours ago",
    triggerCount: 142,
  },
  {
    id: 2,
    title: "Slack Alert",
    description: "Post to Slack on high-priority tickets",
    isActive: true,
    lastRun: "5 mins ago",
    triggerCount: 89,
  },
  {
    id: 3,
    title: "Data Sync",
    description: "Sync CRM data every hour",
    isActive: false,
    lastRun: "1 day ago",
    triggerCount: 456,
  },
  {
    id: 4,
    title: "Report Generator",
    description: "Generate weekly reports on Monday",
    isActive: true,
    lastRun: "3 days ago",
    triggerCount: 24,
  },
  {
    id: 5,
    title: "Lead Scoring",
    description: "Auto-score leads based on activity",
    isActive: true,
    lastRun: "Just now",
    triggerCount: 1203,
  },
  {
    id: 6,
    title: "Task Assignment",
    description: "Assign tasks to team based on workload",
    isActive: false,
    lastRun: "1 week ago",
    triggerCount: 67,
  },
];

const AutomationGrid = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {mockAutomations.map((automation, index) => (
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