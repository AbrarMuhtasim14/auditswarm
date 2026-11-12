import sys
import os
import asyncio
from pathlib import Path

# Add project root and backend dir to sys.path so both 'app.*' and 'backend.app.*' work
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

# Handle imports whether package is 'backend.app' or 'app'
try:
    from backend.app.graph import stream_audit_events
    from backend.app.contracts import get_contract_code
    from backend.app.near_adapter import get_all_agent_wallets_sync
    from backend.app.config import SWARM_ACCOUNTS
except ImportError:
    from app.graph import stream_audit_events
    from app.contracts import get_contract_code
    from app.near_adapter import get_all_agent_wallets_sync
    from app.config import SWARM_ACCOUNTS

console = Console()

AGENT_COLORS = {
    "Coordinator": "bold cyan",
    "Static Hunter": "bold green",
    "Economic Exploit Agent": "bold yellow",
    "Red-Team Critic": "bold magenta",
    "Arbiter": "bold gold1",
    "Treasury Payout Engine": "bold blue"
}

AGENT_ICONS = {
    "Coordinator": "🛡️",
    "Static Hunter": "🔍",
    "Economic Exploit Agent": "⚡",
    "Red-Team Critic": "🥊",
    "Arbiter": "⚖️",
    "Treasury Payout Engine": "💰"
}

def print_header():
    title = Text("NEAR MULTI-AGENT ADVERSARIAL AUDIT SWARM", style="bold white on blue", justify="center")
    subtitle = Text("Autonomous Smart Contract Auditing via LangGraph & NEAR Testnet Settlement\nTrack 05: Swarms | Track 06: Security | Track 07: Agents", style="cyan", justify="center")
    console.print(Panel(Text.assemble(title, "\n", subtitle), border_style="bright_blue", box=box.DOUBLE))

def display_wallets():
    table = Table(title="NEAR Testnet Swarm Agent Topology & Wallets", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("Agent / Node", style="bold")
    table.add_column("Audit Role", style="dim")
    table.add_column("NEAR Testnet Account", style="bright_yellow")
    table.add_column("Live Balance (NEAR)", justify="right", style="green")
    table.add_column("Explorer Link", style="blue")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        progress.add_task(description="Querying NEAR Testnet RPC (https://rpc.testnet.near.org)...", total=None)
        wallets = get_all_agent_wallets_sync()

    for w in wallets:
        table.add_row(
            w.role,
            w.role,
            w.account_id,
            f"{w.balance_near} NEAR",
            f"https://testnet.nearblocks.io/address/{w.account_id}"
        )
    console.print(table)
    console.print()

async def run_cli_audit(contract_name: str = "VulnerableVault.rs", bounty_near: float = 1.0):
    print_header()
    display_wallets()

    code = get_contract_code(contract_name)
    if not code:
        console.print(f"[red]Error: Contract {contract_name} could not be loaded.[/red]")
        return

    console.print(Panel(
        f"[bold]Target Contract:[/bold] [yellow]{contract_name}[/yellow] ({len(code.splitlines())} lines)\n"
        f"[bold]Bounty Settlement Pool:[/bold] [green]{bounty_near} NEAR[/green]\n"
        f"[bold]Execution Mode:[/bold] [cyan]LangGraph Adversarial Debate (5 Autonomous Agents)[/cyan]",
        title="Audit Configuration",
        border_style="yellow"
    ))
    console.print()

    final_result = None

    async for event in stream_audit_events(contract_name, code, bounty_near, execute_real_payout=True):
        evt_type = event["event"]
        data = event["data"]

        if evt_type == "agent_start":
            agent = data["agent"]
            role = data["role"]
            icon = AGENT_ICONS.get(agent, "🤖")
            color = AGENT_COLORS.get(agent, "bold white")
            console.print(f"{icon} [{color}]Entering Phase:[/{color}] [bold]{agent}[/bold] ({role})...")

        elif evt_type == "debate_message":
            sender = data["sender"]
            msg = data["message"]
            icon = AGENT_ICONS.get(sender, "💬")
            color = AGENT_COLORS.get(sender, "bold white")
            
            panel_style = "green" if "Hunter" in sender else ("yellow" if "Economic" in sender else ("magenta" if "Critic" in sender else ("gold1" if "Arbiter" in sender else "cyan")))
            console.print(Panel(
                f"[white]{msg}[/white]",
                title=f"{icon} [{color}]{sender}[/{color}]",
                border_style=panel_style,
                box=box.ROUNDED
            ))

        elif evt_type == "findings_updated":
            # Just small indicator
            pass

        elif evt_type == "audit_complete":
            final_result = data

    if not final_result:
        console.print("[red]Audit failed to complete cleanly.[/red]")
        return

    # Print Findings Table
    console.print()
    findings = final_result.get("findings", [])
    findings_table = Table(title="Arbitrated Vulnerability Catalog", box=box.HEAVY_EDGE, header_style="bold yellow")
    findings_table.add_column("ID", style="bold", width=12)
    findings_table.add_column("Severity", justify="center", width=10)
    findings_table.add_column("Title", style="bold white", width=32)
    findings_table.add_column("Category", style="dim", width=22)
    findings_table.add_column("Status", justify="center", width=12)
    findings_table.add_column("Remediation", style="green", width=35)

    sev_styles = {
        "CRITICAL": "[bold white on red] CRITICAL [/bold white on red]",
        "HIGH": "[bold red] HIGH [/bold red]",
        "MEDIUM": "[bold yellow] MEDIUM [/bold yellow]",
        "LOW": "[bold cyan] LOW [/bold cyan]",
        "INFO": "[dim] INFO [/dim]"
    }

    status_styles = {
        "VERIFIED": "[bold green]VERIFIED[/bold green]",
        "DISMISSED": "[dim red]DISMISSED[/dim red]",
        "CHALLENGED": "[yellow]CHALLENGED[/yellow]",
        "PROPOSED": "[blue]PROPOSED[/blue]"
    }

    for f in findings:
        sev_badge = sev_styles.get(f["severity"], f["severity"])
        st_badge = status_styles.get(f["status"], f["status"])
        findings_table.add_row(
            f["id"],
            sev_badge,
            f["title"][:32],
            f["category"][:22],
            st_badge,
            (f.get("remediation") or "N/A")[:35]
        )
    console.print(findings_table)

    # Print Payout Table
    console.print()
    payouts = final_result.get("payouts", [])
    payout_table = Table(title="Consensus Bounty Distribution (NEAR Testnet)", box=box.DOUBLE_EDGE, header_style="bold green")
    payout_table.add_column("Agent", style="bold")
    payout_table.add_column("Contribution %", justify="right", style="cyan")
    payout_table.add_column("Reward (NEAR)", justify="right", style="bold green")
    payout_table.add_column("Testnet Account ID", style="bright_yellow")
    payout_table.add_column("Status", justify="center", style="green")
    payout_table.add_column("Tx Hash / Verification", style="blue")

    for p in payouts:
        payout_table.add_row(
            p["agent_name"],
            f"{p['contribution_percent']:.1f}%",
            f"{p['reward_near']:.4f} NEAR",
            p["account_id"],
            f"[bold green]{p['status']}[/bold green]",
            p.get("tx_hash", "Pending")[:28] + "..." if p.get("tx_hash") and len(p.get("tx_hash")) > 28 else (p.get("tx_hash") or "N/A")
        )
    console.print(payout_table)

    # Final summary banner
    verdict = final_result.get("arbiter_verdict", {})
    score = verdict.get("security_score", 0)
    rating = verdict.get("security_rating", "UNKNOWN")
    console.print()
    console.print(Panel(
        f"[bold]Consensus Score:[/bold] [{ 'red' if score < 50 else 'green' }]{score}/100 ({rating})[/{ 'red' if score < 50 else 'green' }]\n"
        f"[bold]Summary:[/bold] {verdict.get('summary', 'Audit complete.')}\n"
        f"[bold]NearBlocks Testnet Explorer:[/bold] https://testnet.nearblocks.io/address/{SWARM_ACCOUNTS['main']}",
        title="Audit Swarm Consensus Summary",
        border_style="gold1",
        box=box.ROUNDED
    ))

def main():
    import argparse
    parser = argparse.ArgumentParser(description="NEAR Multi-Agent Adversarial Audit Swarm CLI")
    parser.add_argument("--contract", "-c", default="VulnerableVault.rs", help="Contract filename in test_contracts/")
    parser.add_argument("--bounty", "-b", type=float, default=0.1, help="Bounty pool in NEAR")
    args = parser.parse_args()

    asyncio.run(run_cli_audit(args.contract, args.bounty))

if __name__ == "__main__":
    main()
