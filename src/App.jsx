import { useState, useEffect } from 'react';
import Layout from './components/Layout';
import LoadingOverlay from './components/LoadingOverlay';
import Dashboard from './views/Dashboard';
import N8nWebview from './views/N8nWebview';
import EnvironmentVariables from './views/EnvironmentVariables';
import SystemTools from './views/SystemTools';
import { useN8nStatus } from './hooks/useN8nStatus';

const VIEWS = {
  dashboard: Dashboard,
  n8n: N8nWebview,
  env: EnvironmentVariables,
  tools: SystemTools,
};

export default function App() {
  const [activeView, setActiveView] = useState('dashboard');
  const { status, message, url, config } = useN8nStatus();

  const isBooting = ['checking', 'starting', 'waiting'].includes(status);
  const isReady = status === 'ready';
  const View = VIEWS[activeView];

  return (
    <>
      {isBooting && <LoadingOverlay message={message} mode={config?.startMode} />}

      <Layout
        activeView={activeView}
        onNavigate={setActiveView}
        n8nStatus={status}
        n8nUrl={url}
      >
        {status === 'error' ? (
          <ErrorState message={message} onRetry={() => window.n8nAPI.retryStart()} />
        ) : (
          <View n8nReady={isReady} n8nUrl={url} />
        )}
      </Layout>
    </>
  );
}

function ErrorState({ message, onRetry }) {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-4 p-8 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-red-500/10 text-red-400">
        <span className="text-2xl">!</span>
      </div>
      <h2 className="text-xl font-semibold">Could not reach n8n</h2>
      <p className="max-w-md text-sm text-gray-400">{message}</p>
      <button type="button" onClick={onRetry} className="btn-primary">
        Retry connection
      </button>
    </div>
  );
}
