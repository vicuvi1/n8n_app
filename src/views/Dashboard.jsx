import {
  HardDrive,
  Activity,
  Cpu,
  MemoryStick,
  Clock,
  Calendar,
  Wifi,
  RefreshCw,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import StatCard from '../components/StatCard';
import { useMetrics } from '../hooks/useMetrics';

function formatUptime(ms) {
  if (!ms) return '—';
  const s = Math.floor(ms / 1000);
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  return `${h}h ${m}m ${sec}s`;
}

function formatDate(iso) {
  if (!iso) return 'Unknown';
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function ApiBadge({ status }) {
  const styles = {
    connected: 'bg-accent-green/10 text-accent-green border-accent-green/20',
    degraded: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    offline: 'bg-red-500/10 text-red-400 border-red-500/20',
  };

  return (
    <span className={`status-badge border ${styles[status] || styles.offline}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${status === 'connected' ? 'bg-accent-green' : status === 'degraded' ? 'bg-amber-400' : 'bg-red-400'}`} />
      {status === 'connected' ? 'API Connected' : status === 'degraded' ? 'Degraded' : 'Offline'}
    </span>
  );
}

export default function Dashboard({ n8nReady }) {
  const { metrics, loading, refresh } = useMetrics(n8nReady);

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <header className="flex shrink-0 items-center justify-between border-b border-surface-border px-8 py-5">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Instance Manager</h1>
          <p className="mt-0.5 text-sm text-gray-500">
            Storage, executions, and system health at a glance
          </p>
        </div>
        <button type="button" onClick={refresh} className="btn-secondary">
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </header>

      <div className="flex-1 overflow-y-auto p-8">
        {loading && !metrics ? (
          <DashboardSkeleton />
        ) : (
          <div className="space-y-8">
            {/* Stat cards */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <StatCard
                title="Total Storage"
                value={metrics?.storage?.totalFormatted ?? '—'}
                subtitle={`DB: ${metrics?.storage?.databaseFormatted ?? '—'}`}
                icon={HardDrive}
                accent="pink"
              />
              <StatCard
                title="Total Executions"
                value={metrics?.executions?.totalExecutions?.toLocaleString() ?? '0'}
                subtitle={`${metrics?.executions?.workflowCount ?? 0} workflows`}
                icon={Activity}
                accent="blue"
              />
              <StatCard
                title="CPU Usage"
                value={metrics?.system?.pid ? `${metrics.system.cpuPercent.toFixed(1)}%` : '—'}
                subtitle={metrics?.system?.pid ? `PID ${metrics.system.pid}` : 'Process not found'}
                icon={Cpu}
                accent="purple"
              />
              <StatCard
                title="Memory"
                value={metrics?.system?.memoryMB ? `${metrics.system.memoryMB} MB` : '—'}
                subtitle="n8n process RAM"
                icon={MemoryStick}
                accent="green"
              />
            </div>

            {/* Charts + instance panel */}
            <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
              <div className="glass-card p-6 xl:col-span-2">
                <h2 className="mb-1 text-sm font-semibold">Execution History</h2>
                <p className="mb-6 text-xs text-gray-500">Daily workflow runs (last 14 days)</p>

                {metrics?.executions?.dailyRuns?.length > 0 ? (
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={metrics.executions.dailyRuns}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
                      <XAxis
                        dataKey="day"
                        tick={{ fill: '#6B7280', fontSize: 11 }}
                        tickFormatter={(v) => v?.slice(5) ?? v}
                        axisLine={false}
                        tickLine={false}
                      />
                      <YAxis
                        tick={{ fill: '#6B7280', fontSize: 11 }}
                        axisLine={false}
                        tickLine={false}
                        width={30}
                      />
                      <Tooltip
                        contentStyle={{
                          background: '#151C2F',
                          border: '1px solid #1F2937',
                          borderRadius: 8,
                          fontSize: 12,
                        }}
                        cursor={{ fill: 'rgba(255,109,90,0.08)' }}
                      />
                      <Bar
                        dataKey="count"
                        fill="#FF6D5A"
                        radius={[4, 4, 0, 0]}
                        maxBarSize={40}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex h-[220px] items-center justify-center text-sm text-gray-500">
                    No execution data found in local database
                  </div>
                )}

                <div className="mt-4 flex gap-4">
                  <div className="flex items-center gap-2 text-sm">
                    <CheckCircle2 size={16} className="text-accent-green" />
                    <span className="text-gray-400">Success:</span>
                    <span className="font-medium">{metrics?.executions?.successCount ?? 0}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <XCircle size={16} className="text-red-400" />
                    <span className="text-gray-400">Errors:</span>
                    <span className="font-medium">{metrics?.executions?.errorCount ?? 0}</span>
                  </div>
                </div>
              </div>

              <div className="glass-card p-6">
                <h2 className="mb-4 text-sm font-semibold">Instance Summary</h2>
                <div className="space-y-4">
                  <SummaryRow
                    icon={Calendar}
                    label="First deployed"
                    value={formatDate(metrics?.instance?.deployDate)}
                  />
                  <SummaryRow
                    icon={Clock}
                    label="Session uptime"
                    value={formatUptime(metrics?.instance?.uptimeMs)}
                  />
                  <SummaryRow
                    icon={Wifi}
                    label="API status"
                    value={<ApiBadge status={metrics?.system?.apiStatus} />}
                  />
                  <SummaryRow
                    icon={HardDrive}
                    label="Data path"
                    value={
                      <span className="truncate font-mono text-[11px] text-gray-400">
                        {metrics?.storage?.dataPath}
                      </span>
                    }
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function SummaryRow({ icon: Icon, label, value }) {
  return (
    <div className="flex items-start gap-3">
      <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-surface-hover text-gray-400">
        <Icon size={16} />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-xs text-gray-500">{label}</p>
        <div className="mt-0.5 text-sm font-medium">{value}</div>
      </div>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="glass-card p-5">
            <div className="skeleton mb-4 h-10 w-10" />
            <div className="skeleton mb-2 h-4 w-24" />
            <div className="skeleton h-8 w-32" />
          </div>
        ))}
      </div>
      <div className="skeleton h-72 w-full rounded-xl" />
    </div>
  );
}
