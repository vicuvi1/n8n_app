const os = require('os');
const path = require('path');

module.exports = {
  /** How n8n is started: 'npx' | 'docker' */
  startMode: 'npx',

  /** Stop n8n on app quit (only if this app started it). */
  stopOnQuit: false,

  n8nHost: '127.0.0.1',
  n8nPort: 5678,

  /** Docker container name when startMode is 'docker'. */
  dockerContainerName: 'n8n',

  /**
   * Local n8n data directory (.n8n folder).
   * Override with N8N_USER_FOLDER env var if you use a custom path.
   */
  n8nDataPath: process.env.N8N_USER_FOLDER || path.join(os.homedir(), '.n8n'),

  portCheckIntervalMs: 2000,
  startupTimeoutMs: 120_000,

  /** How often the dashboard refreshes live metrics (ms). */
  metricsPollIntervalMs: 3000,
};
