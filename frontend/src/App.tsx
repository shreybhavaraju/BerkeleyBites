import { AppProvider, useApp } from './context/AppContext';
import { AppShell } from './components/layout/AppShell';
import { ChatPanel } from './components/chat/ChatPanel';
import { MenuBrowser } from './components/menu/MenuBrowser';

function LoadingScreen() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="text-4xl mb-4">🍽️</div>
        <h1 className="text-xl font-semibold text-berkeley mb-2">BerkeleyBites</h1>
        <p className="text-gray-500 text-sm">Loading today's menu...</p>
        <div className="mt-4 flex justify-center gap-1">
          <span className="w-2 h-2 bg-berkeley rounded-full animate-bounce" />
          <span
            className="w-2 h-2 bg-berkeley rounded-full animate-bounce"
            style={{ animationDelay: '0.1s' }}
          />
          <span
            className="w-2 h-2 bg-berkeley rounded-full animate-bounce"
            style={{ animationDelay: '0.2s' }}
          />
        </div>
      </div>
    </div>
  );
}

function ErrorScreen({ error }: { error: string }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center max-w-md px-4">
        <div className="text-4xl mb-4">😕</div>
        <h1 className="text-xl font-semibold text-gray-900 mb-2">
          Something went wrong
        </h1>
        <p className="text-gray-500 text-sm mb-4">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-berkeley text-white rounded-lg text-sm font-medium hover:bg-berkeley-light transition-colors"
        >
          Try Again
        </button>
      </div>
    </div>
  );
}

function AppContent() {
  const { isLoading, error } = useApp();

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (error) {
    return <ErrorScreen error={error} />;
  }

  return (
    <AppShell>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* AI Chat Panel */}
        <ChatPanel />

        {/* Menu Browser */}
        <div id="menu-section">
          <MenuBrowser />
        </div>
      </div>
    </AppShell>
  );
}

function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}

export default App;
