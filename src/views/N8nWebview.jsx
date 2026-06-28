import { useEffect, useRef } from 'react';
import { ExternalLink } from 'lucide-react';

export default function N8nWebview({ n8nReady, n8nUrl }) {
  const webviewRef = useRef(null);

  useEffect(() => {
    if (!n8nReady || !webviewRef.current || !n8nUrl) return;

    const webview = webviewRef.current;
    webview.src = n8nUrl;
  }, [n8nReady, n8nUrl]);

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <header className="flex shrink-0 items-center justify-between border-b border-surface-border px-6 py-3">
        <div>
          <h1 className="text-sm font-semibold">n8n Dashboard</h1>
          <p className="text-xs text-gray-500">Embedded workflow editor</p>
        </div>
        {n8nReady && (
          <a
            href={n8nUrl}
            target="_blank"
            rel="noreferrer"
            className="btn-secondary py-1.5 text-xs"
          >
            <ExternalLink size={14} />
            Open in browser
          </a>
        )}
      </header>

      <div className="relative flex-1 bg-surface">
        {!n8nReady ? (
          <div className="flex h-full items-center justify-center text-sm text-gray-500">
            Waiting for n8n to start…
          </div>
        ) : (
          <webview
            ref={webviewRef}
            src="about:blank"
            className="h-full w-full"
            partition="persist:n8n"
            allowpopups="true"
            style={{ display: 'inline-flex' }}
          />
        )}
      </div>
    </div>
  );
}
