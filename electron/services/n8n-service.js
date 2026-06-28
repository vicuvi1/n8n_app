const net = require('net');
const { spawn } = require('child_process');
const http = require('http');
const config = require('../../config');

let n8nChildProcess = null;
let n8nStartedByApp = false;
let portCheckTimer = null;
let startupTimeoutTimer = null;
let instanceStartedAt = null;

const N8N_URL = `http://${config.n8nHost}:${config.n8nPort}`;

const START_COMMANDS = {
  npx: {
    command: process.platform === 'win32' ? 'npx.cmd' : 'npx',
    args: ['n8n'],
    shell: true,
  },
  docker: {
    command: 'docker',
    args: ['start', config.dockerContainerName],
    shell: true,
  },
};

function isPortOpen(host = config.n8nHost, port = config.n8nPort) {
  return new Promise((resolve) => {
    const socket = net.createConnection({ host, port });
    socket.setTimeout(1500);
    socket.once('connect', () => {
      socket.destroy();
      resolve(true);
    });
    socket.once('timeout', () => {
      socket.destroy();
      resolve(false);
    });
    socket.once('error', () => resolve(false));
  });
}

function checkApiHealth() {
  return new Promise((resolve) => {
    const req = http.get(`${N8N_URL}/healthz`, { timeout: 2000 }, (res) => {
      resolve(res.statusCode === 200 ? 'connected' : 'degraded');
    });
    req.on('error', () => resolve('offline'));
    req.on('timeout', () => {
      req.destroy();
      resolve('offline');
    });
  });
}

function clearTimers() {
  if (portCheckTimer) {
    clearInterval(portCheckTimer);
    portCheckTimer = null;
  }
  if (startupTimeoutTimer) {
    clearTimeout(startupTimeoutTimer);
    startupTimeoutTimer = null;
  }
}

function startN8nProcess() {
  const startConfig = START_COMMANDS[config.startMode];
  if (!startConfig) {
    throw new Error(`Unknown startMode "${config.startMode}". Use "npx" or "docker".`);
  }

  n8nChildProcess = spawn(startConfig.command, startConfig.args, {
    shell: startConfig.shell,
    detached: true,
    stdio: 'ignore',
    windowsHide: true,
  });

  n8nChildProcess.unref();
  n8nStartedByApp = true;
  instanceStartedAt = Date.now();

  n8nChildProcess.on('error', (err) => {
    throw err;
  });
}

async function waitForN8n(onStatus) {
  clearTimers();
  onStatus?.({ status: 'checking', message: 'Checking if n8n is running…', url: N8N_URL });

  if (await isPortOpen()) {
    if (!instanceStartedAt) instanceStartedAt = Date.now();
    onStatus?.({ status: 'ready', message: 'n8n is already running.', url: N8N_URL });
    return;
  }

  onStatus?.({ status: 'starting', message: `Starting n8n via ${config.startMode}…`, url: N8N_URL });

  try {
    startN8nProcess();
  } catch (err) {
    onStatus?.({ status: 'error', message: err.message, url: N8N_URL });
    return;
  }

  onStatus?.({ status: 'waiting', message: 'Waiting for n8n to become ready…', url: N8N_URL });

  startupTimeoutTimer = setTimeout(() => {
    clearTimers();
    onStatus?.({
      status: 'error',
      message: `Timed out after ${config.startupTimeoutMs / 1000}s.`,
      url: N8N_URL,
    });
  }, config.startupTimeoutMs);

  portCheckTimer = setInterval(async () => {
    if (await isPortOpen()) {
      clearTimers();
      onStatus?.({ status: 'ready', message: 'n8n is ready.', url: N8N_URL });
    }
  }, config.portCheckIntervalMs);
}

async function stopN8nIfNeeded() {
  if (!config.stopOnQuit || !n8nStartedByApp) return;

  if (config.startMode === 'docker') {
    spawn('docker', ['stop', config.dockerContainerName], {
      shell: true,
      stdio: 'ignore',
      windowsHide: true,
    });
    return;
  }

  if (n8nChildProcess?.pid) {
    try {
      if (process.platform === 'win32') {
        spawn('taskkill', ['/pid', String(n8nChildProcess.pid), '/T', '/F'], {
          shell: true,
          stdio: 'ignore',
          windowsHide: true,
        });
      } else {
        process.kill(-n8nChildProcess.pid, 'SIGTERM');
      }
    } catch {
      // Process may have already exited.
    }
  }
}

function getN8nState() {
  return {
    url: N8N_URL,
    port: config.n8nPort,
    startMode: config.startMode,
    stopOnQuit: config.stopOnQuit,
    startedByApp: n8nStartedByApp,
    instanceStartedAt,
    dataPath: config.n8nDataPath,
  };
}

module.exports = {
  isPortOpen,
  checkApiHealth,
  waitForN8n,
  stopN8nIfNeeded,
  clearTimers,
  getN8nState,
  N8N_URL,
};
