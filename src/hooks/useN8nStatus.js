import { useState, useEffect } from 'react';

export function useN8nStatus() {
  const [status, setStatus] = useState('checking');
  const [message, setMessage] = useState('Initializing…');
  const [url, setUrl] = useState('http://localhost:5678');
  const [config, setConfig] = useState(null);

  useEffect(() => {
    window.n8nAPI.getConfig().then(setConfig);

    const unsubscribe = window.n8nAPI.onStatus(({ status: s, message: m, url: u }) => {
      setStatus(s);
      setMessage(m);
      if (u) setUrl(u);
    });

    return unsubscribe;
  }, []);

  return { status, message, url, config };
}
