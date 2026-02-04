interface AgentSummaryCardProps {
  icon: string;
  title: string;
  points: string[];
}

export function AgentSummaryCard({ icon, title, points }: AgentSummaryCardProps) {
  return (
    <div className="bg-slate-warm rounded-lg p-3 border border-slate-border hover:border-berkeley-gold/30 transition-colors">
      <h4 className="font-semibold text-sm flex items-center gap-2 mb-2 text-berkeley">
        <span className="w-6 h-6 bg-white rounded-md flex items-center justify-center shadow-sm text-xs">
          {icon}
        </span>
        <span>{title}</span>
      </h4>
      <ul className="text-sm text-gray-600 space-y-1.5 pl-8">
        {points.map((point, i) => (
          <li key={i} className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 bg-berkeley-gold rounded-full mt-1.5 flex-shrink-0" />
            <span className="leading-relaxed">{point}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
