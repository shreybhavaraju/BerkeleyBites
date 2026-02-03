import { useProfile } from '../../hooks/useProfile';

export function ProfileSummary() {
  const { getProfileSummary } = useProfile();
  const summary = getProfileSummary();

  if (summary.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-3">
        <p className="text-gray-500 text-sm italic">No restrictions set</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-3">
      <div className="flex flex-wrap gap-2">
        {summary.map((item, index) => (
          <span
            key={index}
            className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-berkeley/10 text-berkeley"
          >
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}
