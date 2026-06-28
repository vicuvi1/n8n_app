import Sidebar from './Sidebar';

export default function Layout({ children, activeView, onNavigate, n8nStatus, n8nUrl }) {
  return (
    <div className="flex h-screen w-screen bg-surface">
      <Sidebar
        activeView={activeView}
        onNavigate={onNavigate}
        n8nStatus={n8nStatus}
        n8nUrl={n8nUrl}
      />
      <main className="flex min-w-0 flex-1 flex-col overflow-hidden">
        {children}
      </main>
    </div>
  );
}
