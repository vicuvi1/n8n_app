export default function LoadingOverlay({ message, mode }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-surface/95 backdrop-blur-md">
      <div className="flex flex-col items-center gap-8 px-8 text-center">
        <div className="relative">
          <div className="h-20 w-20 rounded-full border-2 border-surface-border" />
          <div className="absolute inset-0 animate-spin-slow rounded-full border-2 border-transparent border-t-accent-pink" />
          <div className="absolute inset-3 animate-pulse-slow rounded-full bg-accent-pink/10" />
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-lg font-bold text-accent-pink">n8</span>
          </div>
        </div>

        <div className="space-y-2">
          <h1 className="text-2xl font-semibold tracking-tight">Starting n8n</h1>
          <p className="max-w-sm text-sm text-gray-400">{message}</p>
          {mode && (
            <p className="text-xs text-gray-600">
              Mode: <span className="font-mono text-gray-400">{mode}</span>
            </p>
          )}
        </div>

        <div className="flex w-64 flex-col gap-2">
          <div className="skeleton h-2 w-full" />
          <div className="skeleton h-2 w-3/4 mx-auto" />
          <div className="skeleton h-2 w-1/2 mx-auto" />
        </div>
      </div>
    </div>
  );
}
