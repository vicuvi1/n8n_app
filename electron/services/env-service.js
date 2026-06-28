const fs = require('fs');
const path = require('path');
const { app } = require('electron');
const config = require('../../config');

const ENV_FILE = () => path.join(app.getPath('userData'), 'n8n-env.json');
const DOTENV_FILE = () => path.join(config.n8nDataPath, '.env');

const DEFAULT_KEYS = [
  'N8N_ENCRYPTION_KEY',
  'N8N_HOST',
  'N8N_PORT',
  'N8N_PROTOCOL',
  'WEBHOOK_URL',
  'N8N_BASIC_AUTH_ACTIVE',
  'N8N_BASIC_AUTH_USER',
  'N8N_BASIC_AUTH_PASSWORD',
  'DB_TYPE',
  'EXECUTIONS_DATA_PRUNE',
  'EXECUTIONS_DATA_MAX_AGE',
];

function readJson(filePath) {
  if (!fs.existsSync(filePath)) return {};
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch {
    return {};
  }
}

function writeJson(filePath, data) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');
}

function parseDotEnv(content) {
  const vars = {};
  for (const line of content.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eq = trimmed.indexOf('=');
    if (eq === -1) continue;
    const key = trimmed.slice(0, eq).trim();
    const value = trimmed.slice(eq + 1).trim().replace(/^["']|["']$/g, '');
    vars[key] = value;
  }
  return vars;
}

function serializeDotEnv(vars) {
  return Object.entries(vars)
    .map(([key, value]) => `${key}=${value}`)
    .join('\n');
}

function getEnvVars() {
  const stored = readJson(ENV_FILE());
  const dotenv = fs.existsSync(DOTENV_FILE())
    ? parseDotEnv(fs.readFileSync(DOTENV_FILE(), 'utf8'))
    : {};

  const merged = { ...dotenv, ...stored };
  const keys = [...new Set([...DEFAULT_KEYS, ...Object.keys(merged)])];

  return keys.map((key) => ({
    key,
    value: merged[key] ?? process.env[key] ?? '',
    source: stored[key] !== undefined ? 'app' : dotenv[key] !== undefined ? 'dotenv' : 'system',
  }));
}

function saveEnvVars(entries) {
  const record = {};
  for (const { key, value } of entries) {
    if (key.trim()) record[key.trim()] = value;
  }
  writeJson(ENV_FILE(), record);

  const dotenvPath = DOTENV_FILE();
  if (fs.existsSync(path.dirname(dotenvPath))) {
    fs.writeFileSync(dotenvPath, serializeDotEnv(record) + '\n', 'utf8');
  }

  return getEnvVars();
}

function addEnvVar(key, value) {
  const current = readJson(ENV_FILE());
  current[key] = value;
  writeJson(ENV_FILE(), current);
  return getEnvVars();
}

function deleteEnvVar(key) {
  const current = readJson(ENV_FILE());
  delete current[key];
  writeJson(ENV_FILE(), current);
  return getEnvVars();
}

module.exports = { getEnvVars, saveEnvVars, addEnvVar, deleteEnvVar };
