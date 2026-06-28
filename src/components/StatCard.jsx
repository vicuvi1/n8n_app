export default function StatCard({ title, value, subtitle, icon: Icon, accent = 'pink', trend }) {
  const accents = {
    pink: 'from-accent-pink/20 to-transparent text-accent-pink',
    green: 'from-accent-green/20 to-transparent text-accent-green',
    blue: 'from-accent-blue/20 to-transparent text-accent-blue',
    purple: 'from-accent-purple/20 to-transparent text-accent-purple',
  };

  return (
    <div className="glass-card group p-5 transition-all duration-300 hover:border-gray-600 hover:shadow-glow">
      <div className="mb-4 flex items-start justify-between">
        <div
          className={`flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br ${accents[accent]}`}
        >
          {Icon && <Icon size={20} strokeWidth={1.75} />}
        </div>
        {trend && (
          <span className="text-xs font-medium text-accent-green">{trend}</span>
        )}
      </div>
      <p className="text-sm font-medium text-gray-400">{title}</p>
      <p className="mt-1 text-2xl font-semibold tracking-tight">{value}</p>
      {subtitle && <p className="mt-1 text-xs text-gray-500">{subtitle}</p>}
    </div>
  );
}
