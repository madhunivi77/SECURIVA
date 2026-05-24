// src/components/admin/AnalyticsCards.jsx
import { Users, MessageSquare, KeyRound, Shield } from "lucide-react";

const analyticsData = [
  {
    title: "Total Users",
    value: "128",
    change: "+12.4% vs last 30 days",
    positive: true,
    icon: Users,
    cardBg: "bg-blue-50",
    iconBg: "bg-blue-100",
    iconColor: "text-blue-600",
  },
  {
    title: "Total Chats",
    value: "542",
    change: "+18.7% vs last 30 days",
    positive: true,
    icon: MessageSquare,
    cardBg: "bg-green-50",
    iconBg: "bg-green-100",
    iconColor: "text-green-600",
  },
  {
    title: "Active Tokens",
    value: "76",
    change: "+8.3% vs last 30 days",
    positive: true,
    icon: KeyRound,
    cardBg: "bg-purple-50",
    iconBg: "bg-purple-100",
    iconColor: "text-purple-600",
  },
  {
    title: "Audit Logs",
    value: "34",
    change: "-4.2% vs last 30 days",
    positive: false,
    icon: Shield,
    cardBg: "bg-orange-50",
    iconBg: "bg-orange-100",
    iconColor: "text-orange-600",
  },
];

const AnalyticsCards = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
      {analyticsData.map((card, index) => {
        const Icon = card.icon;

        return (
          <div
            key={index}
            className={`${card.cardBg} rounded-xl p-5 shadow-sm border border-gray-100`}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm font-medium">
                  {card.title}
                </p>
                <h2 className="text-3xl font-bold text-gray-800">
                  {card.value}
                </h2>
                <p
                  className={`text-sm font-medium mt-1 ${
                    card.positive ? "text-green-600" : "text-red-500"
                  }`}
                >
                  {card.change}
                </p>
              </div>

              <div
                className={`${card.iconBg} ${card.iconColor} p-3 rounded-full`}
              >
                <Icon size={22} />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default AnalyticsCards;