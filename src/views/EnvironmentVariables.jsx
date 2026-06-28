import { useState, useEffect } from 'react';
import { Plus, Save, Trash2, Variable } from 'lucide-react';

export default function EnvironmentVariables() {
  const [vars, setVars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [newKey, setNewKey] = useState('');
  const [newValue, setNewValue] = useState('');
  const [message, setMessage] = useState('');

  const load = async () => {
    setLoading(true);
    const data = await window.n8nAPI.getEnvVars();
    setVars(data);
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, []);

  const updateVar = (index, field, value) => {
    setVars((prev) => prev.map((v, i) => (i === index ? { ...v, [field]: value } : v)));
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage('');
    try {
      const saved = await window.n8nAPI.saveEnvVars(
        vars.map(({ key, value }) => ({ key, value }))
      );
      setVars(saved);
      setMessage('Saved to app config and ~/.n8n/.env');
    } catch (err) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleAdd = async () => {
    if (!newKey.trim()) return;
    await window.n8nAPI.addEnvVar(newKey.trim(), newValue);
    setNewKey('');
    setNewValue('');
    load();
  };

  const handleDelete = async (key) => {
    await window.n8nAPI.deleteEnvVar(key);
    load();
  };

  const sourceColors = {
    app: 'text-accent-pink',
    dotenv: 'text-accent-blue',
    system: 'text-gray-500',
  };

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <header className="flex shrink-0 items-center justify-between border-b border-surface-border px-8 py-5">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Environment Variables</h1>
          <p className="mt-0.5 text-sm text-gray-500">
            Manage n8n configuration keys (saved to local .env)
          </p>
        </div>
        <button type="button" onClick={handleSave} disabled={saving} className="btn-primary">
          <Save size={16} />
          {saving ? 'Saving…' : 'Save all'}
        </button>
      </header>

      <div className="flex-1 overflow-y-auto p-8">
        {message && (
          <div className="mb-4 rounded-lg border border-accent-green/20 bg-accent-green/10 px-4 py-2 text-sm text-accent-green">
            {message}
          </div>
        )}

        <div className="glass-card mb-6 p-4">
          <p className="mb-3 text-xs font-medium uppercase tracking-wider text-gray-500">
            Add variable
          </p>
          <div className="flex flex-wrap gap-3">
            <input
              className="input-field max-w-xs flex-1 font-mono"
              placeholder="N8N_ENCRYPTION_KEY"
              value={newKey}
              onChange={(e) => setNewKey(e.target.value)}
            />
            <input
              className="input-field max-w-sm flex-1"
              placeholder="value"
              value={newValue}
              onChange={(e) => setNewValue(e.target.value)}
            />
            <button type="button" onClick={handleAdd} className="btn-secondary">
              <Plus size={16} />
              Add
            </button>
          </div>
        </div>

        {loading ? (
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="skeleton h-14 w-full" />
            ))}
          </div>
        ) : (
          <div className="space-y-2">
            {vars.map((v, i) => (
              <div
                key={v.key}
                className="glass-card flex items-center gap-3 p-3 transition-colors hover:border-gray-600"
              >
                <Variable size={16} className="shrink-0 text-gray-600" />
                <input
                  className="input-field w-48 shrink-0 font-mono text-xs"
                  value={v.key}
                  onChange={(e) => updateVar(i, 'key', e.target.value)}
                />
                <input
                  className="input-field min-w-0 flex-1 font-mono text-xs"
                  value={v.value}
                  onChange={(e) => updateVar(i, 'value', e.target.value)}
                  type={v.key.toLowerCase().includes('password') || v.key.toLowerCase().includes('key') ? 'password' : 'text'}
                />
                <span className={`shrink-0 text-[10px] uppercase ${sourceColors[v.source]}`}>
                  {v.source}
                </span>
                <button
                  type="button"
                  onClick={() => handleDelete(v.key)}
                  className="shrink-0 rounded-lg p-2 text-gray-500 transition-colors hover:bg-red-500/10 hover:text-red-400"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
