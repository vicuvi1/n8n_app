import {
  LayoutDashboard,
  Workflow,
  Variable,
  Wrench,
  Zap,
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'n8n', label: 'n8n Webview', icon: Workflow },
  { id: 'env', label: 'Environment', icon: Variable },
  { id: 'tools', label: 'System Tools', icon: Wrench },
];

function StatusDot({ status }) {
  const colors = {
    ready: 'bg-accent-green shadow-glow-green',
    error: 'bg-red-500',
    checking: 'bg-amber-400 animate-pulse',
    starting: 'bg-amber-400 animate-pulse',
    waiting: 'bg-amber-400 animate-pulse',
  };

  return (
    <span
      className={`h-2 w-2 rounded-full ${colors[status] || 'bg-gray-500'}`}
    />
  );
}

export default function Sidebar({ activeView, onNavigate, n8nStatus, n8nUrl }) {
  return (
    <aside className="flex w-60 shrink-0 flex-col border-r border-surface-border bg-surface-raised/50">
      <div className="flex items-center gap-3 border-b border-surface-border px-5 py-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-accent-pink to-orange-400 text-sm font-bold text-white shadow-glow">
          n8
        </div>
        <div>
          <p className="text-sm font-semibold tracking-tight">Command Center</p>
          <p className="text-[11px] text-gray-500">n8n Instance Manager</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 p-3">
        {NAV_ITEMS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            onClick={() => onNavigate(id)}
            className={`nav-item ${activeView === id ? 'nav-item-active' : ''}`}
          >
            <Icon size={18} strokeWidth={1.75} />
            {label}
          </button>
        ))}
      </nav>

      <div className="border-t border-surface-border p-4">
        <div className="glass-card p-3">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-xs font-medium text-gray-400">Instance</span>
            <StatusDot status={n8nStatus} />
          </div>
          <p className="truncate font-mono text-[11px] text-gray-500">{n8nUrl}</p>
          <div className="mt-2 flex items-center gap-1.5 text-[11px] text-gray-500">
            <Zap size={12} className="text-accent-green" />
            {n8nStatus === 'ready' ? 'Online' : n8nStatus === 'error' ? 'Offline' : 'Booting…'}
          </div>
        </div>
      </div>
    </aside>
  );
}
