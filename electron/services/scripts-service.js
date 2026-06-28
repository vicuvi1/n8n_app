const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { app } = require('electron');

const SCRIPTS_FILE = () => path.join(app.getPath('userData'), 'saved-scripts.json');

const DEFAULT_SCRIPTS = [
  {
    id: 'restart-n8n',
    name: 'Restart n8n (npx)',
    command: process.platform === 'win32' ? 'npx.cmd n8n' : 'npx n8n',
    description: 'Launch n8n via npx in the background',
  },
  {
    id: 'docker-logs',
    name: 'Docker Logs (n8n)',
    command: 'docker logs -f --tail 50 n8n',
    description: 'Stream recent n8n container logs',
  },
  {
    id: 'open-data-folder',
    name: 'Open .n8n Folder',
    command:
      process.platform === 'win32'
        ? 'explorer %USERPROFILE%\\.n8n'
        : process.platform === 'darwin'
          ? 'open ~/.n8n'
          : 'xdg-open ~/.n8n',
    description: 'Open the local n8n data directory',
  },
];

function readScripts() {
  const file = SCRIPTS_FILE();
  if (!fs.existsSync(file)) {
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, JSON.stringify(DEFAULT_SCRIPTS, null, 2), 'utf8');
    return DEFAULT_SCRIPTS;
  }
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch {
    return DEFAULT_SCRIPTS;
  }
}

function writeScripts(scripts) {
  fs.writeFileSync(SCRIPTS_FILE(), JSON.stringify(scripts, null, 2), 'utf8');
  return scripts;
}

function saveScript(script) {
  const scripts = readScripts();
  const idx = scripts.findIndex((s) => s.id === script.id);
  const entry = {
    id: script.id || `script-${Date.now()}`,
    name: script.name,
    command: script.command,
    description: script.description || '',
  };

  if (idx >= 0) scripts[idx] = entry;
  else scripts.push(entry);

  return writeScripts(scripts);
}

function deleteScript(id) {
  const scripts = readScripts().filter((s) => s.id !== id);
  return writeScripts(scripts);
}

function runScript(command) {
  return new Promise((resolve) => {
    const child = spawn(command, [], {
      shell: true,
      windowsHide: false,
      detached: true,
      stdio: 'ignore',
    });
    child.unref();
    resolve({ success: true, message: `Executed: ${command}` });
  });
}

module.exports = { readScripts, saveScript, deleteScript, runScript };
