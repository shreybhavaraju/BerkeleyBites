import { useState, useRef, useEffect } from 'react';
import { ProfileSummary } from '../profile/ProfileSummary';
import { ProfileEditor } from '../profile/ProfileEditor';
import { FeedbackStats } from '../profile/FeedbackStats';

function ProfileDropdown({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        onClose();
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      ref={dropdownRef}
      className="absolute right-0 top-full mt-2 w-80 bg-white rounded-xl shadow-xl border border-slate-border overflow-hidden animate-slide-down z-50"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-berkeley to-berkeley-light px-4 py-3">
        <h3 className="text-white font-semibold">Your Profile</h3>
        <p className="text-white/70 text-xs mt-0.5">Dietary preferences & feedback</p>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4 max-h-[70vh] overflow-y-auto">
        <section>
          <h4 className="text-xs font-bold text-berkeley uppercase tracking-wider mb-2 flex items-center gap-2">
            <span className="w-1 h-4 bg-berkeley-gold rounded-full" />
            Active Filters
          </h4>
          <ProfileSummary />
          <ProfileEditor />
        </section>

        <div className="h-px bg-slate-border" />

        <section>
          <h4 className="text-xs font-bold text-berkeley uppercase tracking-wider mb-2 flex items-center gap-2">
            <span className="w-1 h-4 bg-berkeley-gold rounded-full" />
            Your Feedback
          </h4>
          <FeedbackStats />
        </section>
      </div>
    </div>
  );
}

export function Header() {
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  });

  return (
    <header className="bg-berkeley text-white sticky top-0 z-40">
      {/* Gold accent bar */}
      <div className="h-1 bg-gradient-to-r from-berkeley-gold via-berkeley-gold-dark to-berkeley-gold" />

      <div className="px-4 md:px-6 py-3">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-berkeley-gold rounded-lg flex items-center justify-center shadow-lg transform hover:scale-105 transition-transform">
              <span className="text-xl">🍽️</span>
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight font-display">
                Berkeley<span className="text-berkeley-gold">Bites</span>
              </h1>
              <p className="text-[10px] text-white/50 uppercase tracking-widest">UC Berkeley Dining</p>
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-3 md:gap-4">
            {/* Date */}
            <time className="text-white/60 text-sm hidden md:block">{today}</time>

            {/* Profile button */}
            <div className="relative">
              <button
                onClick={() => setIsProfileOpen(!isProfileOpen)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${
                  isProfileOpen
                    ? 'bg-berkeley-gold text-berkeley'
                    : 'bg-white/10 hover:bg-white/20 text-white'
                }`}
              >
                <div className="w-7 h-7 bg-berkeley-gold/20 rounded-full flex items-center justify-center">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <svg className={`w-4 h-4 transition-transform ${isProfileOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <ProfileDropdown isOpen={isProfileOpen} onClose={() => setIsProfileOpen(false)} />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
