import { AppProvider, useApp } from './context/AppContext';
import { AppShell } from './components/layout/AppShell';
import { ChatPanel } from './components/chat/ChatPanel';
import { MenuBrowser } from './components/menu/MenuBrowser';

function LoadingScreen() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-warm">
      <div className="text-center">
        {/* Logo animation */}
        <div className="relative">
          <div className="w-20 h-20 bg-berkeley rounded-2xl flex items-center justify-center mx-auto shadow-xl">
            <span className="text-4xl">🍽️</span>
          </div>
          <div className="absolute -bottom-1 -right-1 w-8 h-8 bg-berkeley-gold rounded-lg flex items-center justify-center shadow-lg animate-bounce">
            <span className="text-sm">✨</span>
          </div>
        </div>

        <h1 className="text-2xl font-bold text-berkeley font-display mt-6">
          Berkeley<span className="text-berkeley-gold">Bites</span>
        </h1>
        <p className="text-gray-500 text-sm mt-1">Loading today's menu...</p>

        {/* Loading bar */}
        <div className="mt-6 w-48 mx-auto">
          <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
            <div className="h-full bg-berkeley-gold rounded-full animate-pulse w-2/3" />
          </div>
        </div>
      </div>
    </div>
  );
}

function ErrorScreen({ error }: { error: string }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-warm">
      <div className="text-center max-w-md px-6">
        <div className="w-20 h-20 bg-error/10 rounded-2xl flex items-center justify-center mx-auto border-2 border-error/20">
          <span className="text-4xl">😕</span>
        </div>
        <h1 className="text-xl font-bold text-berkeley font-display mt-6">
          Something went wrong
        </h1>
        <p className="text-gray-500 text-sm mt-2">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-6 px-6 py-3 bg-berkeley text-white rounded-xl font-semibold hover:bg-berkeley-light transition-all hover:shadow-lg"
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
      <div className="max-w-4xl mx-auto space-y-8">
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
