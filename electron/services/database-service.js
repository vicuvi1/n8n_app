const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const initSqlJs = require('sql.js');
const config = require('../../config');

function runCommand(command, args) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      shell: true,
      windowsHide: true,
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    let stdout = '';
    let stderr = '';

    child.stdout?.on('data', (d) => {
      stdout += d.toString();
    });
    child.stderr?.on('data', (d) => {
      stderr += d.toString();
    });

    child.on('close', (code) => {
      if (code === 0) resolve({ stdout, stderr });
      else reject(new Error(stderr || stdout || `Exit code ${code}`));
    });

    child.on('error', reject);
  });
}

async function vacuumDatabase(dbPath) {
  const SQL = await initSqlJs();
  const buffer = fs.readFileSync(dbPath);
  const db = new SQL.Database(buffer);

  const before = fs.statSync(dbPath).size;
  db.run('VACUUM');
  const exported = db.export();
  db.close();

  fs.writeFileSync(dbPath, Buffer.from(exported));
  const after = fs.statSync(dbPath).size;

  return { before, after, freed: before - after };
}

async function pruneOldExecutions(dbPath, maxAgeDays = 30) {
  const SQL = await initSqlJs();
  const buffer = fs.readFileSync(dbPath);
  const db = new SQL.Database(buffer);

  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - maxAgeDays);
  const cutoffIso = cutoff.toISOString();

  let deleted = 0;
  try {
    db.run(`DELETE FROM execution_entity WHERE startedAt < ?`, [cutoffIso]);
    deleted = db.getRowsModified();
  } catch {
    try {
      db.run(`DELETE FROM execution_entity WHERE id NOT IN (
        SELECT id FROM execution_entity ORDER BY id DESC LIMIT 500
      )`);
      deleted = db.getRowsModified();
    } catch {
      deleted = 0;
    }
  }

  db.run('VACUUM');
  const exported = db.export();
  db.close();
  fs.writeFileSync(dbPath, Buffer.from(exported));

  return { deleted, maxAgeDays };
}

async function optimizeDatabase(options = {}) {
  const dataPath = config.n8nDataPath;
  const dbPath = path.join(dataPath, 'database.sqlite');
  const results = { steps: [] };

  if (!fs.existsSync(dbPath)) {
    throw new Error(`Database not found at ${dbPath}`);
  }

  const beforeSize = fs.statSync(dbPath).size;

  // Try official n8n prune CLI first.
  try {
    const npx = process.platform === 'win32' ? 'npx.cmd' : 'npx';
    const maxAge = options.maxAgeDays || 30;
    await runCommand(npx, ['n8n', 'prune:executions', `--max-age=${maxAge}`]);
    results.steps.push({ name: 'n8n prune:executions', success: true });
  } catch (err) {
    results.steps.push({ name: 'n8n prune:executions', success: false, note: err.message });
    const prune = await pruneOldExecutions(dbPath, options.maxAgeDays || 30);
    results.steps.push({
      name: 'sqlite manual prune',
      success: true,
      deleted: prune.deleted,
    });
  }

  try {
    const vacuum = await vacuumDatabase(dbPath);
    results.steps.push({
      name: 'sqlite VACUUM',
      success: true,
      freedBytes: vacuum.freed,
    });
  } catch (err) {
    results.steps.push({ name: 'sqlite VACUUM', success: false, note: err.message });
  }

  const afterSize = fs.statSync(dbPath).size;
  results.beforeBytes = beforeSize;
  results.afterBytes = afterSize;
  results.freedBytes = beforeSize - afterSize;

  return results;
}

module.exports = { optimizeDatabase };
