/**
 * Cross-platform setup script for AuditSwarm.
 * Sets up backend Python dependencies and frontend Node dependencies.
 */
const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('🚀 [AuditSwarm] Running full project setup...\n');

const rootDir = path.resolve(__dirname, '..');
const backendDir = path.join(rootDir, 'backend');
const frontendDir = path.join(rootDir, 'frontend');

// 1. Backend Setup
console.log('📦 [1/2] Setting up Backend dependencies...');
let uvFound = false;
try {
  const uvCheck = spawnSync('uv', ['--version'], { shell: true });
  if (uvCheck.status === 0) {
    uvFound = true;
  }
} catch (_) {}

if (uvFound) {
  console.log('⚡ Found uv package manager. Installing backend dependencies via uv...');
  const uvInstall = spawnSync('uv', ['pip', 'install', '-r', 'requirements.txt'], {
    cwd: backendDir,
    stdio: 'inherit',
    shell: true,
  });
  if (uvInstall.status !== 0) {
    console.warn('⚠️  uv pip install exited with non-zero status. Trying uv sync...');
    spawnSync('uv', ['sync'], { cwd: backendDir, stdio: 'inherit', shell: true });
  }
} else {
  console.log('🐍 uv not found in PATH. Using python -m pip...');
  spawnSync('python', ['-m', 'pip', 'install', '-r', 'requirements.txt'], {
    cwd: backendDir,
    stdio: 'inherit',
    shell: true,
  });
}

// 2. Frontend Setup
console.log('\n📦 [2/2] Setting up Frontend dependencies...');
if (fs.existsSync(frontendDir)) {
  const npmInstall = spawnSync('npm', ['install'], {
    cwd: frontendDir,
    stdio: 'inherit',
    shell: true,
  });
  if (npmInstall.status === 0) {
    console.log('✅ Frontend dependencies installed successfully.');
  } else {
    console.warn('⚠️  npm install in frontend exited with code', npmInstall.status);
  }
} else {
  console.log('ℹ️  Frontend directory not found yet.');
}

console.log('\n🎉 [AuditSwarm] Setup complete! Run `npm run dev` or `npm run demo`.');
