const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const initSqlJs = require('sql.js');
const config = require('../../config');
const { isPortOpen, checkApiHealth } = require('./n8n-service');

async function getDirSize(dirPath) {
  let total = 0;

  if (!fs.existsSync(dirPath)) {
    return 0;
  }

  const entries = fs.readdirSync(dirPath, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dirPath, entry.name);
    if (entry.isDirectory()) {
      total += await getDirSize(fullPath);
    } else if (entry.isFile()) {
      try {
        total += fs.statSync(fullPath).size;
      } catch {
        // Skip locked files.
      }
    }
  }

  return total;
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / 1024 ** i).toFixed(i > 0 ? 1 : 0)} ${units[i]}`;
}

function findPidOnPort(port = config.n8nPort) {
  try {
    if (process.platform === 'win32') {
      const output = execSync(`netstat -ano | findstr :${port}`, {
        encoding: 'utf8',
        windowsHide: true,
      });
      const line = output
        .split('\n')
        .map((l) => l.trim())
        .find((l) => l.includes('LISTENING'));
      if (!line) return null;
      const parts = line.trim().split(/\s+/);
      return parseInt(parts[parts.length - 1], 10) || null;
    }

    const output = execSync(`lsof -ti :${port}`, { encoding: 'utf8' });
    return parseInt(output.trim().split('\n')[0], 10) || null;
  } catch {
    return null;
  }
}

function getProcessStats(pid) {
  if (!pid) {
    return { cpuPercent: 0, memoryMB: 0, pid: null };
  }

  try {
    if (process.platform === 'win32') {
      const ps = execSync(
        `powershell -NoProfile -Command "(Get-Process -Id ${pid} -ErrorAction SilentlyContinue | Select-Object CPU,WorkingSet | ConvertTo-Json)"`,
        { encoding: 'utf8', windowsHide: true }
      );
      const data = JSON.parse(ps.trim() || '{}');
      return {
        pid,
        cpuPercent: Number(data.CPU) || 0,
        memoryMB: Math.round((Number(data.WorkingSet) || 0) / (1024 * 1024)),
      };
    }

    const ps = execSync(`ps -p ${pid} -o %cpu=,rss=`, { encoding: 'utf8' });
    const [cpu, rss] = ps.trim().split(/\s+/);
    return {
      pid,
      cpuPercent: parseFloat(cpu) || 0,
      memoryMB: Math.round((parseInt(rss, 10) || 0) / 1024),
    };
  } catch {
    return { cpuPercent: 0, memoryMB: 0, pid };
  }
}

async function readExecutionStats(dbPath) {
  const empty = {
    totalExecutions: 0,
    successCount: 0,
    errorCount: 0,
    dailyRuns: [],
    workflowCount: 0,
  };

  if (!fs.existsSync(dbPath)) return empty;

  try {
    const SQL = await initSqlJs();
    const buffer = fs.readFileSync(dbPath);
    const db = new SQL.Database(buffer);

    const tables = db.exec("SELECT name FROM sqlite_master WHERE type='table'");
    const tableNames = tables[0]?.values?.map((r) => r[0]) || [];

    if (!tableNames.includes('execution_entity')) {
      db.close();
      return empty;
    }

    const total = db.exec('SELECT COUNT(*) FROM execution_entity');
    const success = db.exec("SELECT COUNT(*) FROM execution_entity WHERE status = 'success'");
    const errors = db.exec("SELECT COUNT(*) FROM execution_entity WHERE status = 'error'");
    const workflows = tableNames.includes('workflow_entity')
      ? db.exec('SELECT COUNT(*) FROM workflow_entity')
      : [];

    let dailyRuns = [];
    try {
      const daily = db.exec(`
        SELECT date(startedAt) as day, COUNT(*) as count
        FROM execution_entity
        WHERE startedAt IS NOT NULL
        GROUP BY date(startedAt)
        ORDER BY day DESC
        LIMIT 14
      `);
      if (daily[0]) {
        dailyRuns = daily[0].values
          .map(([day, count]) => ({ day, count }))
          .reverse();
      }
    } catch {
      // Column names may differ across n8n versions.
    }

    db.close();

    return {
      totalExecutions: total[0]?.values[0][0] || 0,
      successCount: success[0]?.values[0][0] || 0,
      errorCount: errors[0]?.values[0][0] || 0,
      workflowCount: workflows[0]?.values[0][0] || 0,
      dailyRuns,
    };
  } catch {
    return empty;
  }
}

function getDeployDate(dataPath) {
  if (!fs.existsSync(dataPath)) return null;

  try {
    const dbPath = path.join(dataPath, 'database.sqlite');
    if (fs.existsSync(dbPath)) {
      return fs.statSync(dbPath).birthtime.toISOString();
    }
    return fs.statSync(dataPath).birthtime.toISOString();
  } catch {
    return null;
  }
}

async function getMetrics(instanceStartedAt) {
  const dataPath = config.n8nDataPath;
  const dbPath = path.join(dataPath, 'database.sqlite');
  const portOpen = await isPortOpen();
  const apiStatus = portOpen ? await checkApiHealth() : 'offline';
  const pid = portOpen ? findPidOnPort() : null;
  const processStats = getProcessStats(pid);

  const [totalSize, dbSize, executionStats] = await Promise.all([
    getDirSize(dataPath),
    fs.existsSync(dbPath) ? fs.statSync(dbPath).size : 0,
    readExecutionStats(dbPath),
  ]);

  const deployDate = getDeployDate(dataPath);
  const uptimeMs = instanceStartedAt && portOpen ? Date.now() - instanceStartedAt : 0;

  return {
    storage: {
      totalBytes: totalSize,
      totalFormatted: formatBytes(totalSize),
      databaseBytes: dbSize,
      databaseFormatted: formatBytes(dbSize),
      dataPath,
    },
    executions: executionStats,
    system: {
      ...processStats,
      portOpen,
      apiStatus,
    },
    instance: {
      deployDate,
      uptimeMs,
      port: config.n8nPort,
      url: `http://${config.n8nHost}:${config.n8nPort}`,
    },
  };
}

module.exports = { getMetrics, formatBytes };
