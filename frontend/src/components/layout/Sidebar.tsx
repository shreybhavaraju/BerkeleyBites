import { ProfileSummary } from '../profile/ProfileSummary';
import { ProfileEditor } from '../profile/ProfileEditor';
import { FeedbackStats } from '../profile/FeedbackStats';
import { MoodSelector } from '../profile/MoodSelector';

export function Sidebar() {
  return (
    <aside className="w-72 bg-gray-50 border-r border-gray-200 p-4 overflow-y-auto hidden lg:block">
      <div className="space-y-6">
        <section>
          <h2 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3">
            Your Profile
          </h2>
          <ProfileSummary />
          <ProfileEditor />
        </section>

        <section>
          <h2 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3">
            Your Feedback
          </h2>
          <FeedbackStats />
        </section>

        <section>
          <h2 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3">
            How are you feeling?
          </h2>
          <MoodSelector />
        </section>
      </div>
    </aside>
  );
}
