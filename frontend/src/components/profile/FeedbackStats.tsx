import { useApp } from '../../context/AppContext';

export function FeedbackStats() {
  const { feedbackStats } = useApp();

  if (!feedbackStats || feedbackStats.total_ratings === 0) {
    return (
      <div className="bg-slate-warm rounded-lg border border-slate-border p-3">
        <p className="text-gray-500 text-sm italic">No feedback yet</p>
        <p className="text-gray-400 text-xs mt-1">Rate dishes to improve recommendations!</p>
      </div>
    );
  }

  const total = feedbackStats.liked_count + feedbackStats.disliked_count;
  const likePercentage = total > 0 ? Math.round((feedbackStats.liked_count / total) * 100) : 0;

  return (
    <div className="bg-slate-warm rounded-lg border border-slate-border p-3">
      {/* Stats row */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 bg-success/10 rounded-lg border border-success/20">
          <svg className="w-4 h-4 text-success" fill="currentColor" viewBox="0 0 20 20">
            <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
          </svg>
          <span className="font-bold text-success">{feedbackStats.liked_count}</span>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg border border-gray-200">
          <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
            <path d="M18 9.5a1.5 1.5 0 11-3 0v-6a1.5 1.5 0 013 0v6zM14 9.667v-5.43a2 2 0 00-1.105-1.79l-.05-.025A4 4 0 0011.055 2H5.64a2 2 0 00-1.962 1.608l-1.2 6A2 2 0 004.44 12H8v4a2 2 0 002 2 1 1 0 001-1v-.667a4 4 0 01.8-2.4l1.4-1.866a4 4 0 00.8-2.4z" />
          </svg>
          <span className="font-bold text-gray-600">{feedbackStats.disliked_count}</span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="mt-3">
        <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-success rounded-full transition-all duration-500"
            style={{ width: `${likePercentage}%` }}
          />
        </div>
        <p className="text-gray-500 text-xs mt-1.5">
          {likePercentage}% liked • {feedbackStats.today_ratings} rated today
        </p>
      </div>
    </div>
  );
}
