import { useState } from 'react';
import { ProfileSummary } from '../profile/ProfileSummary';
import { ProfileEditor } from '../profile/ProfileEditor';
import { FeedbackStats } from '../profile/FeedbackStats';
import { MoodSelector } from '../profile/MoodSelector';

export function MobileNav() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Mobile bottom navigation bar */}
      <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-2 z-40">
        <div className="flex items-center justify-around">
          <button
            onClick={() => setIsOpen(true)}
            className="flex flex-col items-center gap-1 px-4 py-2 text-gray-600 hover:text-berkeley transition-colors"
          >
            <span className="text-xl">👤</span>
            <span className="text-xs">Profile</span>
          </button>
          <button
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            className="flex flex-col items-center gap-1 px-4 py-2 text-gray-600 hover:text-berkeley transition-colors"
          >
            <span className="text-xl">🤖</span>
            <span className="text-xs">AI Chat</span>
          </button>
          <button
            onClick={() =>
              document
                .getElementById('menu-section')
                ?.scrollIntoView({ behavior: 'smooth' })
            }
            className="flex flex-col items-center gap-1 px-4 py-2 text-gray-600 hover:text-berkeley transition-colors"
          >
            <span className="text-xl">🍽️</span>
            <span className="text-xs">Menu</span>
          </button>
        </div>
      </nav>

      {/* Slide-over panel */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/30 z-40 lg:hidden"
            onClick={() => setIsOpen(false)}
          />

          {/* Panel */}
          <div className="fixed inset-y-0 left-0 w-80 bg-white z-50 lg:hidden overflow-y-auto shadow-xl">
            <div className="p-4">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold text-gray-900">Settings</h2>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-6">
                <section>
                  <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3">
                    Your Profile
                  </h3>
                  <ProfileSummary />
                  <ProfileEditor />
                </section>

                <section>
                  <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3">
                    Your Feedback
                  </h3>
                  <FeedbackStats />
                </section>

                <section>
                  <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3">
                    How are you feeling?
                  </h3>
                  <MoodSelector />
                </section>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
}
