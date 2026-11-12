const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

const FFMPEG_PATH = "D:\\HyperFrames_Demo\\bin\\ffmpeg.exe";
const OUTPUT_DIR = path.join(__dirname, '../recordings');

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

const sleep = (ms) => new Promise((res) => setTimeout(res, ms));

async function main() {
  console.log("🎬 Recording NEAR Audit Swarm Demo Video (1080p 60fps)...");

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const context = await browser.newContext({
    recordVideo: {
      dir: OUTPUT_DIR,
      size: { width: 1920, height: 1080 },
    },
    viewport: { width: 1920, height: 1080 },
  });

  const page = await context.newPage();

  // Inject visible animated mouse cursor
  await page.addInitScript(() => {
    window.addEventListener('DOMContentLoaded', () => {
      const c = document.createElement('div');
      c.id = 'demo-cursor';
      c.style.cssText = 'width:22px;height:22px;border:2px solid #06b6d4;background:rgba(6,182,212,0.45);border-radius:50%;position:fixed;pointer-events:none;z-index:999999;transform:translate(-50%,-50%);box-shadow:0 0 12px #06b6d4;transition:transform 0.08s ease;';
      document.body.appendChild(c);
      window.addEventListener('mousemove', (e) => {
        c.style.left = e.clientX + 'px';
        c.style.top = e.clientY + 'px';
      });
      window.addEventListener('mousedown', () => {
        c.style.transform = 'translate(-50%,-50%) scale(0.65)';
        c.style.background = 'rgba(244,63,94,0.7)';
      });
      window.addEventListener('mouseup', () => {
        c.style.transform = 'translate(-50%,-50%) scale(1)';
        c.style.background = 'rgba(6,182,212,0.45)';
      });
    });
  });

  console.log("1. Opening Dashboard...");
  await page.goto('http://127.0.0.1:3000', { waitUntil: 'domcontentloaded' });
  await sleep(2500);

  console.log("2. Selecting Preset 1: Vault Inflation Attack...");
  await page.mouse.move(500, 75, { steps: 10 });
  await sleep(400);
  const preset1 = page.getByRole('button', { name: 'Preset 1: Vault Inflation Attack' });
  if (await preset1.isVisible()) {
    await preset1.click();
    await sleep(1500);
  }

  console.log("3. Touring Swarm Topology DAG...");
  await page.mouse.move(240, 700, { steps: 12 });
  await sleep(800);
  await page.mouse.move(140, 730, { steps: 8 });
  await sleep(600);
  await page.mouse.move(340, 730, { steps: 8 });
  await sleep(600);
  await page.mouse.move(240, 810, { steps: 8 });
  await sleep(800);

  console.log("4. Launching Multi-Agent Adversarial Audit...");
  const launchBtn = page.getByRole('button', { name: 'Launch Multi-Agent Adversarial Audit' });
  await launchBtn.click();
  await sleep(2000);

  console.log("5. Watching LangGraph Agents Stream Debate Turns...");
  for (let i = 0; i < 6; i++) {
    await sleep(4500);
    await page.evaluate(() => {
      const scrollables = document.querySelectorAll('.custom-scrollbar');
      scrollables.forEach(s => s.scrollTop = s.scrollHeight);
    });
  }

  console.log("6. Testing Filter Tabs...");
  const tabs = ['hunter', 'economic', 'critic', 'arbiter', 'all'];
  for (const t of tabs) {
    try {
      const btn = page.getByRole('button', { name: t, exact: true });
      if (await btn.isVisible()) {
        await btn.click();
        await sleep(900);
      }
    } catch {}
  }

  console.log("7. Opening Vulnerability Deep-Dive Drawer...");
  try {
    const diffBtn = page.locator('button:has-text("Deep-Dive Diff →")').first();
    if (await diffBtn.isVisible()) {
      await diffBtn.click();
      await sleep(2000);

      const copyPatch = page.getByRole('button', { name: 'Copy Patch' });
      if (await copyPatch.isVisible()) {
        await copyPatch.click();
        await sleep(1000);
      }

      const closeDrawer = page.getByRole('button', { name: 'Done Reviewing' });
      if (await closeDrawer.isVisible()) {
        await closeDrawer.click();
        await sleep(1000);
      }
    }
  } catch {}

  console.log("8. Generating Cryptographic Audit Certificate & Badge...");
  try {
    const certBtn = page.getByRole('button', { name: 'Generate Cryptographic Audit Certificate & Badge' });
    if (await certBtn.isVisible()) {
      await certBtn.click();
      await sleep(2000);

      const copyBadge = page.getByRole('button', { name: 'Copy README Badge' });
      if (await copyBadge.isVisible()) {
        await copyBadge.click();
        await sleep(1200);
      }

      const closeModal = page.getByRole('button', { name: 'Close' });
      if (await closeModal.isVisible()) {
        await closeModal.click();
        await sleep(1000);
      }
    }
  } catch {}

  console.log("9. Final Overview Showcase...");
  await page.mouse.move(960, 540, { steps: 15 });
  await sleep(3000);

  console.log("10. Finalizing Video Stream...");
  const videoObj = page.video();
  await page.close();

  const tempVideoPath = await videoObj.path();
  console.log(`Temp video written: ${tempVideoPath}`);

  const targetWebm = path.join(OUTPUT_DIR, 'near_audit_swarm_demo.webm');
  const targetMp4 = path.join(OUTPUT_DIR, 'near_audit_swarm_demo.mp4');

  await videoObj.saveAs(targetWebm);
  console.log(`✅ WebM Video saved: ${targetWebm}`);

  await context.close();
  await browser.close();

  // Transcode to MP4 via FFmpeg
  if (fs.existsSync(FFMPEG_PATH)) {
    console.log("🎞️ Transcoding to MP4 (H.264)...");
    try {
      execSync(`"${FFMPEG_PATH}" -y -i "${targetWebm}" -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p "${targetMp4}"`, {
        stdio: 'inherit'
      });
      console.log(`🎉 MP4 Video successfully generated: ${targetMp4}`);
    } catch (e) {
      console.error("FFmpeg transcode error:", e.message);
    }
  }

  console.log("🌟 DEMO VIDEO GENERATION COMPLETE 🌟");
}

main().catch(console.error);
