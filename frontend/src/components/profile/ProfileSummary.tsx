import { useProfile } from '../../hooks/useProfile';

export function ProfileSummary() {
  const { getProfileSummary } = useProfile();
  const summary = getProfileSummary();

  if (summary.length === 0) {
    return (
      <div className="bg-slate-warm rounded-lg p-3 border border-slate-border">
        <p className="text-gray-500 text-sm italic">No dietary restrictions set</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-warm rounded-lg p-3 border border-slate-border">
      <div className="flex flex-wrap gap-2">
        {summary.map((item, index) => (
          <span
            key={index}
            className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold bg-berkeley/10 text-berkeley border border-berkeley/20"
          >
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}
