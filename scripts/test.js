/**
 * Cross-platform Automated Test Runner for AuditSwarm.
 * Runs pytest test suite (FastAPI backend + NEAR testnet client) and frontend linting.
 */
const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('🧪 [AuditSwarm] Running Complete Automated Test Suite...\n');

const rootDir = path.resolve(__dirname, '..');
const frontendDir = path.join(rootDir, 'frontend');

let hasFailures = false;

// 1. Pytest suite
console.log('🔍 [1/2] Running Backend & NEAR Protocol Pytest Suite...');
let uvFound = false;
try {
  const uvCheck = spawnSync('uv', ['--version'], { shell: true });
  if (uvCheck.status === 0) uvFound = true;
} catch (_) {}

const pyCmd = uvFound ? 'uv' : 'python';
const pyArgs = uvFound ? ['run', 'pytest', '-v'] : ['-m', 'pytest', '-v'];

const testPy = spawnSync(pyCmd, pyArgs, {
  cwd: rootDir,
  stdio: 'inherit',
  shell: true,
});

if (testPy.status !== 0) {
  console.error('❌ Pytest suite failed with code:', testPy.status);
  hasFailures = true;
} else {
  console.log('✅ Backend & NEAR Protocol test suite passed.\n');
}

// 2. Frontend Validation
console.log('🔍 [2/2] Running Frontend Lint & Type Validation...');
if (fs.existsSync(frontendDir)) {
  const feLint = spawnSync('npm', ['run', 'lint'], {
    cwd: frontendDir,
    stdio: 'inherit',
    shell: true,
  });
  if (feLint.status !== 0) {
    console.error('❌ Frontend validation reported errors.');
    hasFailures = true;
  } else {
    console.log('✅ Frontend lint validation passed.');
  }
}

console.log('\n🏁 [AuditSwarm] All test suites completed successfully!');
process.exit(hasFailures ? 1 : 0);
