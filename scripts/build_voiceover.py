import asyncio
import edge_tts
import os
import time

VOICE = "en-US-ChristopherNeural"

SEGMENTS = [
    {
        "id": "seg1",
        "start_ms": 500,
        "text": "Welcome to AuditSwarm, the autonomous multi-agent security protocol built for NEAR Hackathon 2026. Every agent controls a dedicated on-chain sub-account with live custody on NEAR testnet."
    },
    {
        "id": "seg2",
        "start_ms": 9500,
        "text": "From the Judge Quick Tour, we load a vulnerable NEAR Rust vault. Notice our LangGraph topology: five specialized agents coordinate, attack, and cross-examine."
    },
    {
        "id": "seg3",
        "start_ms": 17500,
        "text": "We launch the adversarial audit with a one NEAR bounty stake. The Swarm Coordinator decomposes the contract AST and routes tasks to the Static Hunter and Economic Exploit agents."
    },
    {
        "id": "seg4",
        "start_ms": 27500,
        "text": "Watch the adversarial debate unfold live. Rather than accepting hallucinations, the Red-Team Critic challenges every exploit against NEAR runtime rules and gas limits."
    },
    {
        "id": "seg5",
        "start_ms": 37500,
        "text": "The Consensus Arbiter weighs surviving proofs, awards findings, and disproves invalid claims. Filter tabs let judges inspect each persona's specific reasoning."
    },
    {
        "id": "seg6",
        "start_ms": 47000,
        "text": "Opening the Deep-Dive Drawer reveals a verified Vault Share Inflation exploit, complete with root-cause analysis and an actionable patch diff."
    },
    {
        "id": "seg7",
        "start_ms": 54200,
        "text": "The Arbiter generates a cryptographic audit certificate, and the treasury settles signed bounty payouts directly on NEAR testnet. AuditSwarm: security beyond boundaries."
    }
]

async def generate_segment(seg):
    path = f"recordings/audio/{seg['id']}.mp3"
    for attempt in range(4):
        try:
            print(f"Generating {seg['id']} (attempt {attempt+1})...")
            comm = edge_tts.Communicate(seg["text"], VOICE, rate="+4%")
            await comm.save(path)
            print(f"✅ Generated {seg['id']}")
            return
        except Exception as e:
            print(f"Error on {seg['id']}: {e}, retrying...")
            await asyncio.sleep(1.5)
    raise RuntimeError(f"Failed to generate {seg['id']}")

async def main():
    os.makedirs("recordings/audio", exist_ok=True)
    for seg in SEGMENTS:
        await generate_segment(seg)
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())
