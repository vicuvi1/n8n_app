const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const config = require('./config');
const n8nService = require('./electron/services/n8n-service');
const metricsService = require('./electron/services/metrics-service');
const envService = require('./electron/services/env-service');
const scriptsService = require('./electron/services/scripts-service');
const databaseService = require('./electron/services/database-service');

const isDev = !app.isPackaged;

let mainWindow = null;

function sendStatus(payload) {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send('n8n-status', payload);
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 920,
    minWidth: 1100,
    minHeight: 700,
    title: 'n8n Command Center',
    backgroundColor: '#0B0F19',
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      webviewTag: true,
    },
  });

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
  } else {
    mainWindow.loadFile(path.join(__dirname, 'dist', 'index.html'));
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    n8nService.waitForN8n(sendStatus);
  });
}

// ─── IPC handlers ────────────────────────────────────────────────────────────

ipcMain.handle('get-config', () => n8nService.getN8nState());

ipcMain.handle('retry-start', () => {
  n8nService.waitForN8n(sendStatus);
});

ipcMain.handle('get-metrics', async () => {
  const state = n8nService.getN8nState();
  return metricsService.getMetrics(state.instanceStartedAt);
});

ipcMain.handle('get-env-vars', () => envService.getEnvVars());

ipcMain.handle('save-env-vars', (_e, entries) => envService.saveEnvVars(entries));

ipcMain.handle('add-env-var', (_e, key, value) => envService.addEnvVar(key, value));

ipcMain.handle('delete-env-var', (_e, key) => envService.deleteEnvVar(key));

ipcMain.handle('get-scripts', () => scriptsService.readScripts());

ipcMain.handle('save-script', (_e, script) => scriptsService.saveScript(script));

ipcMain.handle('delete-script', (_e, id) => scriptsService.deleteScript(id));

ipcMain.handle('run-script', (_e, command) => scriptsService.runScript(command));

ipcMain.handle('optimize-database', (_e, options) => databaseService.optimizeDatabase(options));

// ─── App lifecycle ─────────────────────────────────────────────────────────────

app.whenReady().then(createWindow);

app.on('window-all-closed', async () => {
  n8nService.clearTimers();
  await n8nService.stopN8nIfNeeded();
  app.quit();
});

app.on('before-quit', async () => {
  n8nService.clearTimers();
  await n8nService.stopN8nIfNeeded();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
