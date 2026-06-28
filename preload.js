const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('n8nAPI', {
  getConfig: () => ipcRenderer.invoke('get-config'),
  retryStart: () => ipcRenderer.invoke('retry-start'),
  getMetrics: () => ipcRenderer.invoke('get-metrics'),
  getEnvVars: () => ipcRenderer.invoke('get-env-vars'),
  saveEnvVars: (entries) => ipcRenderer.invoke('save-env-vars', entries),
  addEnvVar: (key, value) => ipcRenderer.invoke('add-env-var', key, value),
  deleteEnvVar: (key) => ipcRenderer.invoke('delete-env-var', key),
  getScripts: () => ipcRenderer.invoke('get-scripts'),
  saveScript: (script) => ipcRenderer.invoke('save-script', script),
  deleteScript: (id) => ipcRenderer.invoke('delete-script', id),
  runScript: (command) => ipcRenderer.invoke('run-script', command),
  optimizeDatabase: (options) => ipcRenderer.invoke('optimize-database', options),
  onStatus: (callback) => {
    const listener = (_event, payload) => callback(payload);
    ipcRenderer.on('n8n-status', listener);
    return () => ipcRenderer.removeListener('n8n-status', listener);
  },
});
