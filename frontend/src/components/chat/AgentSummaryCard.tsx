interface AgentSummaryCardProps {
  icon: string;
  title: string;
  points: string[];
}

export function AgentSummaryCard({ icon, title, points }: AgentSummaryCardProps) {
  return (
    <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
      <h4 className="font-medium text-sm flex items-center gap-2 mb-2 text-berkeley">
        <span>{icon}</span>
        <span>{title}</span>
      </h4>
      <ul className="text-sm text-gray-600 space-y-1">
        {points.map((point, i) => (
          <li key={i} className="flex items-start gap-1.5">
            <span className="text-berkeley-gold mt-0.5">•</span>
            <span>{point}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
