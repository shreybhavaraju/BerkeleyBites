import { useApp } from '../../context/AppContext';

export function FeedbackStats() {
  const { feedbackStats } = useApp();

  if (!feedbackStats || feedbackStats.total_ratings === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-3">
        <p className="text-gray-500 text-sm italic">No feedback yet</p>
        <p className="text-gray-400 text-xs mt-1">Rate some dishes to get started!</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-3">
      <div className="flex items-center gap-4 text-sm">
        <div className="flex items-center gap-1">
          <span className="text-lg">👍</span>
          <span className="font-medium text-success">{feedbackStats.liked_count}</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="text-lg">👎</span>
          <span className="font-medium text-error">{feedbackStats.disliked_count}</span>
        </div>
      </div>
      <p className="text-gray-500 text-xs mt-2">
        {feedbackStats.today_ratings} ratings today
      </p>
    </div>
  );
}
