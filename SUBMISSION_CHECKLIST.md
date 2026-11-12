# Submission Checklist — NEAR Hackathon 2026

**Hard Deadline:** November 14, 2026 at 23:59 UTC (**November 15, 2026 at 05:59 AM BST**)

---

## 1. Pre-Submission Decisions & Assets
- [x] **Project Name**: `AuditSwarm`
- [x] **Team Lead Name**: `AuditSwarm Lead`
- [x] **Contact Email**: `auditswarm@nearhackathon.io`
- [x] **Team Size**: `2 - 4`
- [x] **Track Selection**: `["swarms", "security", "agents"]`
  - Selected Tracks: **Track 05 (Swarms)**, **Track 06 (Security)**, **Track 07 (Agents)**
- [x] **NEAR Mainnet Address**: `auditswarm.near` (Testnet: `auditswarm-9003.testnet`)
- [x] **Project Pitch (`idea`)**: (Concise 3-part description, 1,280 characters):
  > Smart contract security auditing is prohibitively expensive ($50k-$250k) and slow, while single-agent LLM scanners produce >45% false positives and miss NEAR-specific asynchronous nuances (Promise callback failures, NEP-145 storage exhaustion, and vault share-inflation math).
  > 
  > We built **AuditSwarm**: an autonomous multi-agent adversarial debate engine powered by LangGraph and NEAR Protocol. Five specialized AI personas—Swarm Coordinator, Static Hunter, Economic Exploit Agent, Red-Team Critic, and Arbiter—engage in multi-turn adversarial rounds to uncover vulnerabilities, formulate exploit scenarios, and cross-examine proposed issues against NEAR runtime specs. Verified findings earn cryptographic consensus scores.
  > 
  > NEAR Protocol makes AuditSwarm uniquely viable through its hierarchical sub-account model (`coordinator`, `hunter`, `critic`, `economic.auditswarm-9003.testnet`). Each autonomous agent holds dedicated on-chain custody and receives real-time, signed micro-bounty payouts via NEAR testnet transfers immediately upon consensus. Audit results and payout receipts are cryptographically anchored on-chain and verifiable via NearBlocks explorer.

---

## 2. Codebase & AI Screening Readiness (Claude Code / Codex)
- [x] **Public GitHub Repository**: Repo structured with root `package.json`, `README.md`, and clean git history.
- [x] **Reproducible `README.md`**:
  - [x] Clear "Quickstart / Run in 2 Minutes" instructions.
  - [x] Zero marketing fluff; clean technical steps ("Run X → See Y").
  - [x] Dependency list and exact environment setup (`uv` + Node.js).
  - [x] Dry-run / Mock mode enabled (allows judges/AI to test without spending real crypto).
- [x] **Open Source License**: Included `LICENSE` (MIT License).
- [x] **Clean Code**: No hardcoded API keys or private keys committed; `.gitignore` guards `.env`, `.env.local`, and `.near-credentials/`.
- [x] **Root NPM Scripts Verified**:
  - `npm run setup`: Installs backend Python packages via uv/pip and frontend npm packages.
  - `npm run demo`: Runs complete 5-agent CLI audit with real NEAR testnet settlement (`uv run python -m app.cli_demo`).
  - `npm test`: Runs automated test suite (backend API tests, NEAR testnet RPC tests, frontend validation).
  - `npm run dev`: Starts FastAPI backend (port 8000) and Next.js dashboard (port 3000) concurrently.

---

## 3. The Demo Post on X (Twitter)
- [ ] Record a 1 to 2 minute clean demo video showing:
  1. Running `npm run demo` in terminal with Rich table output, debate turns, and live testnet transaction hashes.
  2. Running `npm run dev` and loading `VulnerableVault.rs` in the 3-column Next.js web dashboard.
  3. Clicking on-chain NearBlocks explorer links to confirm real testnet transaction confirmations.
- [ ] Publish public tweet on X:
  - Mention it was built at **NEAR HACKATHON**.
  - Tag `@NEARProtocol` and `#NEARHackathon` (optional: `@NearBuilders` and `@NearLegion`).
  - Attach video/screenshots.
  - Include GitHub repository link.
- [ ] Copy the tweet link (e.g., `https://x.com/username/status/...`).

---

## 4. Final Submission Execution
- [x] Generate unique UUID for `requestId`:
  ```bash
  node -e "console.log(crypto.randomUUID())"
  ```
- [x] Validate JSON body (**Ensure NO `"website"` key is present — it is an anti-spam honeypot!**).
- [ ] Submit via curl or web form at `https://nearhackathon.com/#apply`:
  ```bash
  curl -sS -X POST https://nearhackathon.com/api/applications \
    -H 'Content-Type: application/json' \
    -d '{
      "requestId": "a7e3b91c-84f2-491a-b328-9128de54109f",
      "projectName": "AuditSwarm",
      "leadName": "AuditSwarm Lead",
      "email": "auditswarm@nearhackathon.io",
      "size": "2 - 4",
      "tracks": ["swarms", "security", "agents"],
      "nearAddress": "auditswarm.near",
      "projectUrl": "https://github.com/<YOUR_ORG>/auditswarm",
      "demoUrl": "https://x.com/<YOUR_HANDLE>/status/<ID>",
      "idea": "Smart contract security auditing is prohibitively expensive ($50k-$250k) and slow, while single-agent LLM scanners produce >45% false positives and miss NEAR-specific asynchronous nuances. We built AuditSwarm: an autonomous multi-agent adversarial debate engine powered by LangGraph and NEAR Protocol. Five specialized AI personas—Swarm Coordinator, Static Hunter, Economic Exploit Agent, Red-Team Critic, and Arbiter—engage in multi-turn adversarial rounds to uncover vulnerabilities, formulate exploit scenarios, and cross-examine proposed issues against NEAR runtime specs. Verified findings earn cryptographic consensus scores. NEAR enables true autonomous agent custody via sub-accounts (coordinator, hunter, critic, economic.auditswarm-9003.testnet) with automated signed micro-bounties settled on-chain.",
      "consent": true
    }'
  ```
- [ ] Verify `201 Created` response.
