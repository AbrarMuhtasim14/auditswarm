# [Project Name]

> Built for **NEAR Hackathon 2026 ("Build Beyond Boundaries")**  
> Tracks: `[e.g., games, agents]`

## 1. Overview & Problem Solved
- **Problem**: [Describe the concrete user or market problem in 2-3 sentences]
- **Solution**: [Describe what this application does]
- **NEAR Integration**: [Explain specifically how NEAR enables this product, e.g., NEP-245 multi-tokens, FastAuth session keys, or NEAR Intents cross-chain settlement]

## 2. Architecture & How NEAR Fits In
```
[User Action] ──> [FastAuth / Session Keys] ──> [Game Loop / Agent Logic]
                                                       │
                                        ┌──────────────┴──────────────┐
                                        ▼                             ▼
                            [NEP-245 Multi-Token]          [NEAR Intents / 1Click]
```
- **Smart Contracts / Standards Used**: [e.g., NEP-245 multi-token standard, NEP-141]
- **Agent Policies**: [e.g., Scoped Function-Call Access Keys, OutLayer custody]
- **Key Modules**:
  - `src/contracts/`: Smart contract logic.
  - `src/agents/`: NPC merchant autonomous pricing and wallet logic.
  - `src/simulation/`: 60-second fast-forward simulation engine.

## 3. Quickstart & Reproducibility ("Do X → See Y")

### Prerequisites
- Node.js >= 18
- npm or pnpm

### Installation
```bash
git clone https://github.com/[your-repo]
cd [your-repo]
npm install
```

### Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(No private keys or mandatory paid API keys required for dry-run verification)*

### Run in Dry-Run / Demo Mode (Zero Crypto Funds Required)
To verify the full economic simulation and merchant mechanics without spending mainnet tokens:
```bash
npm run demo
```
**Expected Output**:
```
[Sim] Initializing 4 NPC Merchants with 100 NEAR and 500 units inventory...
[Sim] Simulating 100 player trades over 7 virtual days...
[Sim] Dynamic pricing engine adjusted Iron Ore: 10 NEAR -> 4.2 NEAR (Oversupply detected).
[Sim] Merchant 'Garrick' ran out of liquidity and closed shop.
[Pass] All economic invariants held.
```

### Run the Web UI
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to interact with the game.

## 4. Verification & Automated Tests
To run the automated test suite:
```bash
npm test
```

## 5. Live Demo & Resources
- **Live Hosted Application**: [https://your-demo-url.vercel.app](https://your-demo-url.vercel.app)
- **Demo Post on X**: [https://x.com/your-handle/status/...](https://x.com/your-handle/status/...)
- **License**: MIT
