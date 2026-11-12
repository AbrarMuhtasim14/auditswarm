/**
 * Cross-platform Demo Runner for AuditSwarm CLI.
 * Runs `uv run python -m app.cli_demo` (or python fallback).
 */
const { spawnSync } = require('child_process');
const path = require('path');

const rootDir = path.resolve(__dirname, '..');
const backendDir = path.join(rootDir, 'backend');

console.log('🤖 [AuditSwarm] Launching Multi-Agent Adversarial Auditing CLI Demo...\n');

let uvFound = false;
try {
  const uvCheck = spawnSync('uv', ['--version'], { shell: true });
  if (uvCheck.status === 0) {
    uvFound = true;
  }
} catch (_) {}

let result;
if (uvFound) {
  result = spawnSync('uv', ['run', 'python', '-m', 'app.cli_demo'], {
    cwd: backendDir,
    stdio: 'inherit',
    shell: true,
  });
} else {
  result = spawnSync('python', ['-m', 'app.cli_demo'], {
    cwd: backendDir,
    stdio: 'inherit',
    shell: true,
  });
}

process.exit(result.status || 0);
