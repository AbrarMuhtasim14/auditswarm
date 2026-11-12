/**
 * Automated High-Fidelity Demo Video Recorder for NEAR Audit Swarm
 * Records a 1080p 60fps walkthrough of the multi-agent adversarial debate UI
 * Transcodes to crystal-clear H.264 MP4 for Hackathon submission & X/Twitter post
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

const FFMPEG_PATH = "D:\\HyperFrames_Demo\\bin\\ffmpeg.exe";
const OUTPUT_DIR = path.join(__dirname, '../recordings');

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function smoothMouseMove(page, targetX, targetY, steps = 12) {
  await page.mouse.move(targetX, targetY, { steps });
  await sleep(150);
}

async function moveAndClick(page, locator) {
  try {
    const box = await locator.boundingBox();
    if (box) {
      await smoothMouseMove(page, box.x + box.width / 2, box.y + box.height / 2, 10);
      await sleep(200);
      await locator.click();
      await sleep(500);
      return true;
    }
  } catch (e) {
    console.warn(`Click warning for locator: ${e.message}`);
  }
  return false;
}

async function main() {
  console.log("🎬 Starting NEAR Audit Swarm Demo Video Recording in 1080p...");

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1920,1080'],
  });

  const context = await browser.newContext({
    recordVideo: {
      dir: OUTPUT_DIR,
      size: { width: 1920, height: 1080 },
    },
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
  });

  const page = await context.newPage();

  // Inject sleek visual cursor helper
  await page.addInitScript(() => {
    window.addEventListener('DOMContentLoaded', () => {
      const cursor = document.createElement('div');
      cursor.id = 'demo-cursor';
      cursor.style.width = '24px';
      cursor.style.height = '24px';
      cursor.style.border = '2px solid #06b6d4';
      cursor.style.backgroundColor = 'rgba(6, 182, 212, 0.4)';
      cursor.style.borderRadius = '50%';
      cursor.style.position = 'fixed';
      cursor.style.pointerEvents = 'none';
      cursor.style.zIndex = '999999';
      cursor.style.transform = 'translate(-50%, -50%)';
      cursor.style.transition = 'transform 0.08s ease, background 0.15s ease, box-shadow 0.15s ease';
      cursor.style.boxShadow = '0 0 14px rgba(6, 182, 212, 0.85)';
      document.body.appendChild(cursor);

      window.addEventListener('mousemove', (e) => {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
      });

      window.addEventListener('mousedown', () => {
        cursor.style.transform = 'translate(-50%, -50%) scale(0.65)';
        cursor.style.backgroundColor = 'rgba(244, 63, 94, 0.75)';
        cursor.style.borderColor = '#f43f5e';
      });

      window.addEventListener('mouseup', () => {
        cursor.style.transform = 'translate(-50%, -50%) scale(1)';
        cursor.style.backgroundColor = 'rgba(6, 182, 212, 0.4)';
        cursor.style.borderColor = '#06b6d4';
      });
    });
  });

  // Scene 1: Initial Landing & Brand Introduction
  console.log("📍 Scene 1: Navigating to NEAR Audit Swarm Dashboard...");
  await page.goto('http://127.0.0.1:3000', { waitUntil: 'domcontentloaded' });
  await sleep(2000);

  // Showcase Header, Status Badges & Testnet Connectivity
  console.log("📍 Exploring Header & NEAR Testnet status...");
  await smoothMouseMove(page, 240, 45, 15);
  await sleep(800);
  await smoothMouseMove(page, 1550, 45, 15);
  await sleep(1000);

  // Scene 2: Judge Quick Tour Banner (Preset 1)
  console.log("📍 Scene 2: Selecting Preset 1: Vault Inflation Attack...");
  const preset1 = page.getByRole('button', { name: 'Preset 1: Vault Inflation Attack' });
  await moveAndClick(page, preset1);
  await sleep(1200);

  // Scene 3: Inspect Code Editor
  console.log("📍 Scene 3: Showcasing VulnerableVault.rs in editor...");
  await smoothMouseMove(page, 850, 280, 12);
  await sleep(600);
  await page.evaluate(() => {
    const el = document.querySelector('textarea');
    if (el) el.scrollTop = 380;
  });
  await sleep(1000);
  await page.evaluate(() => {
    const el = document.querySelector('textarea');
    if (el) el.scrollTop = 0;
  });
  await sleep(800);

  // Scene 4: Swarm Topology Interactive SVG DAG
  console.log("📍 Scene 4: Interactive SVG Swarm Topology DAG...");
  await smoothMouseMove(page, 240, 720, 15);
  await sleep(800);
  // Hover over Static Hunter node
  await smoothMouseMove(page, 150, 750, 10);
  await sleep(600);
  // Hover over Economic Agent node
  await smoothMouseMove(page, 330, 750, 10);
  await sleep(600);
  // Hover over Red-Team Critic node
  await smoothMouseMove(page, 240, 820, 10);
  await sleep(800);

  // Scene 5: Launching Multi-Agent Adversarial Audit
  console.log("📍 Scene 5: Launching Multi-Agent Adversarial Audit...");
  const launchBtn = page.getByRole('button', { name: 'Launch Multi-Agent Adversarial Audit' });
  await moveAndClick(page, launchBtn);
  await sleep(1500);

  // Wait for LangGraph agents to stream debate turns
  console.log("📍 Streaming live multi-agent debate turns...");
  const startTime = Date.now();
  while (Date.now() - startTime < 42000) {
    await sleep(4000);
    // Smooth scroll down the debate stream to highlight active messages
    await page.evaluate(() => {
      const scrollable = document.querySelectorAll('.custom-scrollbar');
      scrollable.forEach(el => {
        el.scrollTop = el.scrollHeight;
      });
    });
  }

  // Scene 6: Filter Tabs Interaction
  console.log("📍 Scene 6: Testing debate stream filters...");
  try {
    const hunterBtn = page.getByRole('button', { name: 'hunter', exact: true });
    await moveAndClick(page, hunterBtn);
    await sleep(1000);

    const econBtn = page.getByRole('button', { name: 'economic', exact: true });
    await moveAndClick(page, econBtn);
    await sleep(1000);

    const criticBtn = page.getByRole('button', { name: 'critic', exact: true });
    await moveAndClick(page, criticBtn);
    await sleep(1000);

    const allBtn = page.getByRole('button', { name: 'all', exact: true });
    await moveAndClick(page, allBtn);
    await sleep(1000);
  } catch (e) {
    console.warn("Filter tabs skipped:", e.message);
  }

  // Scene 7: Deep-Dive Vulnerability & Diff Drawer
  console.log("📍 Scene 7: Opening Deep-Dive Vulnerability & Diff Drawer...");
  try {
    const diffBtn = page.locator('button:has-text("Deep-Dive Diff →")').first();
    if (await diffBtn.isVisible()) {
      await moveAndClick(page, diffBtn);
      await sleep(2000);

      // Copy remediation patch in drawer
      const copyPatchBtn = page.getByRole('button', { name: 'Copy Patch' });
      if (await copyPatchBtn.isVisible()) {
        await moveAndClick(page, copyPatchBtn);
        await sleep(1000);
      }

      // Done reviewing / Close drawer
      const closeDrawerBtn = page.getByRole('button', { name: 'Done Reviewing' });
      if (await closeDrawerBtn.isVisible()) {
        await moveAndClick(page, closeDrawerBtn);
        await sleep(1000);
      }
    }
  } catch (e) {
    console.warn("Drawer interaction skipped:", e.message);
  }

  // Scene 8: Cryptographic Audit Certificate & README Badge Modal
  console.log("📍 Scene 8: Generating Cryptographic Audit Certificate & Badge...");
  try {
    const certBtn = page.getByRole('button', { name: 'Generate Cryptographic Audit Certificate & Badge' });
    await moveAndClick(page, certBtn);
    await sleep(2200);

    // Click Copy README Badge
    const copyBadgeBtn = page.getByRole('button', { name: 'Copy README Badge' });
    if (await copyBadgeBtn.isVisible()) {
      await moveAndClick(page, copyBadgeBtn);
      await sleep(1500);
    }

    // Close Modal
    const closeModalBtn = page.getByRole('button', { name: 'Close' });
    if (await closeModalBtn.isVisible()) {
      await moveAndClick(page, closeModalBtn);
      await sleep(1200);
    }
  } catch (e) {
    console.warn("Certificate modal interaction skipped:", e.message);
  }

  // Scene 9: Preset 3 - Production Fortress (Clean Contract Verification)
  console.log("📍 Scene 9: Testing Preset 3 - SecureEscrow.rs...");
  const preset3 = page.getByRole('button', { name: 'Preset 3: Production Fortress' });
  await moveAndClick(page, preset3);
  await sleep(2000);

  // Scene 10: Smooth Final Showcase & Wrap-up
  console.log("📍 Scene 10: Final overview & wrap-up...");
  await smoothMouseMove(page, 960, 540, 20);
  await sleep(3500);

  // Finish video recording
  console.log("💾 Closing browser to flush recorded video...");
  await context.close();
  await browser.close();

  // Find generated webm file in recordings/
  const files = fs.readdirSync(OUTPUT_DIR).filter(f => f.endsWith('.webm'));
  if (files.length === 0) {
    console.error("❌ No webm video found in recordings/");
    return;
  }

  // Pick the latest webm
  const latestWebm = files.sort((a, b) => {
    return fs.statSync(path.join(OUTPUT_DIR, b)).mtimeMs - fs.statSync(path.join(OUTPUT_DIR, a)).mtimeMs;
  })[0];

  const webmPath = path.join(OUTPUT_DIR, latestWebm);
  const targetWebmPath = path.join(OUTPUT_DIR, 'near_audit_swarm_demo.webm');
  const mp4Path = path.join(OUTPUT_DIR, 'near_audit_swarm_demo.mp4');

  fs.copyFileSync(webmPath, targetWebmPath);
  console.log(`✅ Raw recording saved to: ${targetWebmPath}`);

  // Transcode to MP4 with FFmpeg if available
  if (fs.existsSync(FFMPEG_PATH)) {
    console.log("🎞️ Transcoding to high-quality MP4 (H.264) via FFmpeg...");
    try {
      execSync(`"${FFMPEG_PATH}" -y -i "${targetWebmPath}" -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p "${mp4Path}"`, {
        stdio: 'inherit',
      });
      console.log(`🎉 Transcoding complete! MP4 saved: ${mp4Path}`);
    } catch (e) {
      console.warn("FFmpeg transcode note:", e.message);
    }
  }

  console.log("\n=======================================================");
  console.log("🌟 DEMO VIDEO RECORDING SUCCESSFULLY COMPLETED! 🌟");
  console.log(`WebM File: ${targetWebmPath}`);
  if (fs.existsSync(mp4Path)) {
    console.log(`MP4 File:  ${mp4Path}`);
  }
  console.log("=======================================================\n");
}

main().catch(console.error);
