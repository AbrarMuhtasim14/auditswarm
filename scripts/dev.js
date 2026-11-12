/**
 * Cross-platform Dev Server Runner for AuditSwarm.
 * Concurrently spawns FastAPI backend (port 8000) and Next.js frontend (port 3000).
 */
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('✨ [AuditSwarm] Starting full-stack development environment...\n');

const rootDir = path.resolve(__dirname, '..');
const backendDir = path.join(rootDir, 'backend');
const frontendDir = path.join(rootDir, 'frontend');

// 1. Backend Server
const backendCmd = 'uv run uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload';
console.log(`[Backend] Starting FastAPI server on http://127.0.0.1:8000 ...`);
const backendProc = spawn(backendCmd, {
  cwd: rootDir,
  shell: true,
  stdio: 'inherit',
  env: { ...process.env, PYTHONPATH: rootDir },
});

// 2. Frontend Server
let frontendProc = null;
if (fs.existsSync(frontendDir)) {
  console.log(`[Frontend] Starting Next.js app on http://localhost:3000 ...`);
  frontendProc = spawn('npm run dev', {
    cwd: frontendDir,
    shell: true,
    stdio: 'inherit',
  });
}

const cleanup = () => {
  console.log('\n🛑 [AuditSwarm] Shutting down development servers...');
  if (backendProc && !backendProc.killed) {
    try { process.kill(backendProc.pid); } catch (_) {}
  }
  if (frontendProc && !frontendProc.killed) {
    try { process.kill(frontendProc.pid); } catch (_) {}
  }
  process.exit(0);
};

process.on('SIGINT', cleanup);
process.on('SIGTERM', cleanup);
