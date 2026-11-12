const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

const FFMPEG_PATH = "D:\\HyperFrames_Demo\\bin\\ffmpeg.exe";
const OUTPUT_DIR = path.join(__dirname, '../recordings');
const AUDIO_MASTER = path.join(OUTPUT_DIR, 'audio/full_voiceover_master.mp3');

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

const sleep = (ms) => new Promise((res) => setTimeout(res, ms));

async function main() {
  console.log("🎬 Recording Narrated NEAR Audit Swarm Demo Video (1080p, 84s with Voiceover & Sound)...");

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

  // Inject visible smooth animated cursor
  await page.addInitScript(() => {
    window.addEventListener('DOMContentLoaded', () => {
      const c = document.createElement('div');
      c.id = 'demo-cursor';
      c.style.cssText = 'width:24px;height:24px;border:2px solid #06b6d4;background:rgba(6,182,212,0.45);border-radius:50%;position:fixed;pointer-events:none;z-index:999999;transform:translate(-50%,-50%);box-shadow:0 0 14px #06b6d4;transition:transform 0.08s ease;';
      document.body.appendChild(c);
      window.addEventListener('mousemove', (e) => {
        c.style.left = e.clientX + 'px';
        c.style.top = e.clientY + 'px';
      });
      window.addEventListener('mousedown', () => {
        c.style.transform = 'translate(-50%,-50%) scale(0.6)';
        c.style.background = 'rgba(244,63,94,0.75)';
      });
      window.addEventListener('mouseup', () => {
        c.style.transform = 'translate(-50%,-50%) scale(1)';
        c.style.background = 'rgba(6,182,212,0.45)';
      });
    });
  });

  // Timeline:
  // [0.0 - 14.0s] Introduction & Header / Agent Cards
  console.log("1. Opening Dashboard [0.0 - 14.0s]...");
  await page.goto('http://127.0.0.1:3000', { waitUntil: 'domcontentloaded' });
  await sleep(2500);

  // Hover over testnet status badge
  await page.mouse.move(700, 36, { steps: 12 });
  await sleep(1500);

  // Hover over agent cards (Coordinator, Hunter, Economic, Critic)
  await page.mouse.move(140, 200, { steps: 10 });
  await sleep(2200);
  await page.mouse.move(140, 330, { steps: 8 });
  await sleep(2200);
  await page.mouse.move(140, 460, { steps: 8 });
  await sleep(2200);
  await page.mouse.move(140, 590, { steps: 8 });
  await sleep(2200);

  // [14.0 - 26.0s] Judge Quick Tour & LangGraph Topology
  console.log("2. Selecting Preset 1 & Exploring Topology [14.0 - 26.0s]...");
  await page.mouse.move(500, 75, { steps: 12 });
  await sleep(600);
  const preset1 = page.getByRole('button', { name: 'Preset 1: Vault Inflation Attack' });
  if (await preset1.isVisible()) {
    await preset1.click();
    await sleep(2500);
  }

  // Move over code editor
  await page.mouse.move(960, 320, { steps: 10 });
  await sleep(2500);

  // Move down to LangGraph Topology DAG
  await page.mouse.move(160, 780, { steps: 10 });
  await sleep(2000);
  await page.mouse.move(260, 840, { steps: 8 });
  await sleep(2000);

  // [26.0 - 38.5s] Launch Multi-Agent Adversarial Audit
  console.log("3. Launching Adversarial Audit [26.0 - 38.5s]...");
  const launchBtn = page.getByRole('button', { name: 'Launch Multi-Agent Adversarial Audit' });
  await page.mouse.move(960, 560, { steps: 12 });
  await sleep(1000);
  await launchBtn.click();
  await sleep(3500);

  // Initial streaming debate
  for (let s = 0; s < 2; s++) {
    await sleep(4000);
    await page.evaluate(() => {
      const scrollables = document.querySelectorAll('.custom-scrollbar');
      scrollables.forEach(el => el.scrollTop = el.scrollHeight);
    });
  }

  // [38.5 - 50.5s] Streaming Debate Rounds & Red-Team Critic Rebuttals
  console.log("4. Streaming Multi-Agent Debate Turns [38.5 - 50.5s]...");
  for (let s = 0; s < 3; s++) {
    await sleep(3800);
    await page.evaluate(() => {
      const scrollables = document.querySelectorAll('.custom-scrollbar');
      scrollables.forEach(el => el.scrollTop = el.scrollHeight);
    });
  }

  // [50.5 - 62.0s] Filtering Turns by Persona
  console.log("5. Testing Filter Tabs [50.5 - 62.0s]...");
  const tabs = ['hunter', 'economic', 'critic', 'arbiter', 'all'];
  for (const t of tabs) {
    try {
      const btn = page.getByRole('button', { name: t, exact: true });
      if (await btn.isVisible()) {
        await btn.click();
        await sleep(2100);
      }
    } catch {}
  }

  // [62.0 - 71.0s] Vulnerability Deep-Dive Drawer
  console.log("6. Opening Deep-Dive Drawer [62.0 - 71.0s]...");
  try {
    const diffBtn = page.locator('button:has-text("Deep-Dive Diff →")').first();
    if (await diffBtn.isVisible()) {
      await diffBtn.click();
      await sleep(3200);

      const copyPatch = page.getByRole('button', { name: 'Copy Patch' });
      if (await copyPatch.isVisible()) {
        await copyPatch.click();
        await sleep(1500);
      }

      const closeDrawer = page.getByRole('button', { name: 'Done Reviewing' });
      if (await closeDrawer.isVisible()) {
        await closeDrawer.click();
        await sleep(1500);
      }
    }
  } catch {}

  // [71.0 - 84.0s] Cryptographic Certificate & Payout Proofs
  console.log("7. Generating Audit Certificate & Payouts [71.0 - 84.0s]...");
  try {
    const certBtn = page.getByRole('button', { name: 'Generate Cryptographic Audit Certificate & Badge' });
    if (await certBtn.isVisible()) {
      await certBtn.click();
      await sleep(3500);

      const copyBadge = page.getByRole('button', { name: 'Copy README Badge' });
      if (await copyBadge.isVisible()) {
        await copyBadge.click();
        await sleep(1800);
      }

      const closeModal = page.getByRole('button', { name: 'Close' });
      if (await closeModal.isVisible()) {
        await closeModal.click();
        await sleep(1500);
      }
    }
  } catch {}

  // Final review of testnet payouts
  await page.mouse.move(1700, 480, { steps: 12 });
  await sleep(4000);

  console.log("8. Finalizing Video Capture...");
  const videoObj = page.video();
  await page.close();

  const tempVideoPath = await videoObj.path();
  console.log(`Temp video written: ${tempVideoPath}`);

  const targetWebm = path.join(OUTPUT_DIR, 'narrated_raw.webm');
  const targetMp4 = path.join(OUTPUT_DIR, 'near_audit_swarm_demo.mp4');

  await videoObj.saveAs(targetWebm);
  console.log(`✅ Raw WebM Video saved: ${targetWebm}`);

  await context.close();
  await browser.close();

  // Combine video with master voiceover audio
  if (fs.existsSync(FFMPEG_PATH) && fs.existsSync(AUDIO_MASTER)) {
    console.log("🎞️ Multiplexing Video and Master Audio (H.264 + AAC)...");
    try {
      execSync(
        `"${FFMPEG_PATH}" -y -i "${targetWebm}" -i "${AUDIO_MASTER}" -c:v libx264 -preset fast -crf 21 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest "${targetMp4}"`,
        { stdio: 'inherit' }
      );
      console.log(`🎉 Narrated MP4 Video Generated Successfully: ${targetMp4}`);
    } catch (e) {
      console.error("FFmpeg transcode error:", e.message);
    }
  }

  console.log("🌟 NARRATED DEMO VIDEO COMPLETE 🌟");
}

main().catch(console.error);
