import { useState, useEffect } from 'react';
import {
  Play,
  Plus,
  Trash2,
  Terminal,
  Database,
  Loader2,
  CheckCircle2,
} from 'lucide-react';

export default function SystemTools() {
  const [scripts, setScripts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);
  const [optimizeResult, setOptimizeResult] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', command: '', description: '' });
  const [runningId, setRunningId] = useState(null);

  const loadScripts = async () => {
    setLoading(true);
    const data = await window.n8nAPI.getScripts();
    setScripts(data);
    setLoading(false);
  };

  useEffect(() => {
    loadScripts();
  }, []);

  const runScript = async (script) => {
    setRunningId(script.id);
    try {
      await window.n8nAPI.runScript(script.command);
    } finally {
      setTimeout(() => setRunningId(null), 1500);
    }
  };

  const saveScript = async () => {
    if (!form.name || !form.command) return;
    await window.n8nAPI.saveScript(form);
    setForm({ name: '', command: '', description: '' });
    setShowForm(false);
    loadScripts();
  };

  const deleteScript = async (id) => {
    await window.n8nAPI.deleteScript(id);
    loadScripts();
  };

  const optimize = async () => {
    setOptimizing(true);
    setOptimizeResult(null);
    try {
      const result = await window.n8nAPI.optimizeDatabase({ maxAgeDays: 30 });
      setOptimizeResult(result);
    } catch (err) {
      setOptimizeResult({ error: err.message });
    } finally {
      setOptimizing(false);
    }
  };

  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / 1024 ** i).toFixed(1)} ${units[i]}`;
  };

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <header className="shrink-0 border-b border-surface-border px-8 py-5">
        <h1 className="text-xl font-semibold tracking-tight">System Tools</h1>
        <p className="mt-0.5 text-sm text-gray-500">
          Quick scripts, automations, and database maintenance
        </p>
      </header>

      <div className="flex-1 overflow-y-auto p-8">
        <div className="grid grid-cols-1 gap-8 xl:grid-cols-2">
          {/* Script launcher */}
          <section>
            <div className="mb-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Terminal size={18} className="text-accent-blue" />
                <h2 className="text-sm font-semibold">Quick Script Launcher</h2>
              </div>
              <button type="button" onClick={() => setShowForm(!showForm)} className="btn-secondary py-1.5 text-xs">
                <Plus size={14} />
                New script
              </button>
            </div>

            {showForm && (
              <div className="glass-card mb-4 space-y-3 p-4">
                <input
                  className="input-field"
                  placeholder="Script name"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
                <input
                  className="input-field font-mono text-xs"
                  placeholder="Command to execute"
                  value={form.command}
                  onChange={(e) => setForm({ ...form, command: e.target.value })}
                />
                <input
                  className="input-field text-xs"
                  placeholder="Description (optional)"
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                />
                <button type="button" onClick={saveScript} className="btn-primary w-full">
                  Save script
                </button>
              </div>
            )}

            {loading ? (
              <div className="space-y-2">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="skeleton h-16 w-full" />
                ))}
              </div>
            ) : (
              <div className="space-y-2">
                {scripts.map((script) => (
                  <div
                    key={script.id}
                    className="glass-card flex items-center gap-4 p-4 transition-all hover:border-gray-600"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium">{script.name}</p>
                      <p className="mt-0.5 truncate font-mono text-[11px] text-gray-500">
                        {script.command}
                      </p>
                      {script.description && (
                        <p className="mt-1 text-xs text-gray-600">{script.description}</p>
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={() => runScript(script)}
                      disabled={runningId === script.id}
                      className="btn-primary shrink-0 py-2"
                    >
                      {runningId === script.id ? (
                        <Loader2 size={16} className="animate-spin" />
                      ) : (
                        <Play size={16} />
                      )}
                      Run
                    </button>
                    {!['restart-n8n', 'docker-logs', 'open-data-folder'].includes(script.id) && (
                      <button
                        type="button"
                        onClick={() => deleteScript(script.id)}
                        className="shrink-0 rounded-lg p-2 text-gray-500 hover:bg-red-500/10 hover:text-red-400"
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Database optimizer */}
          <section>
            <div className="mb-4 flex items-center gap-2">
              <Database size={18} className="text-accent-purple" />
              <h2 className="text-sm font-semibold">Database Optimizer</h2>
            </div>

            <div className="glass-card p-6">
              <p className="text-sm text-gray-400">
                Prune old execution history and run SQLite VACUUM to reclaim disk space
                from your local n8n database.
              </p>

              <ul className="mt-4 space-y-2 text-xs text-gray-500">
                <li>• Runs <code className="text-gray-400">n8n prune:executions</code> (30-day max age)</li>
                <li>• Falls back to manual SQLite cleanup if CLI unavailable</li>
                <li>• Compacts database file with VACUUM</li>
              </ul>

              <button
                type="button"
                onClick={optimize}
                disabled={optimizing}
                className="btn-primary mt-6 w-full"
              >
                {optimizing ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    Optimizing…
                  </>
                ) : (
                  <>
                    <Database size={16} />
                    Run optimization
                  </>
                )}
              </button>

              {optimizeResult && !optimizeResult.error && (
                <div className="mt-4 rounded-lg border border-accent-green/20 bg-accent-green/10 p-4">
                  <div className="mb-2 flex items-center gap-2 text-sm font-medium text-accent-green">
                    <CheckCircle2 size={16} />
                    Optimization complete
                  </div>
                  <p className="text-xs text-gray-400">
                    Freed {formatBytes(optimizeResult.freedBytes)} ·{' '}
                    {formatBytes(optimizeResult.beforeBytes)} → {formatBytes(optimizeResult.afterBytes)}
                  </p>
                  <ul className="mt-2 space-y-1">
                    {optimizeResult.steps?.map((step, i) => (
                      <li key={i} className="text-[11px] text-gray-500">
                        {step.success ? '✓' : '✗'} {step.name}
                        {step.deleted != null && ` (${step.deleted} rows)`}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {optimizeResult?.error && (
                <div className="mt-4 rounded-lg border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-400">
                  {optimizeResult.error}
                </div>
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
