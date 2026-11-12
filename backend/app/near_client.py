"""
near_client.py - NEAR Protocol Client & Testnet Integration for AuditSwarm.

Provides real testnet balance querying via JSON-RPC, signed token transfers using
the NEAR CLI (C:\\Users\\USER\\.cargo\\bin\\near.exe), credential resolution,
and test contract loading for multi-agent adversarial audits.
"""

import os
import re
import json
import logging
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
import urllib.request
import urllib.error

from backend.app.config import NEAR_RPC_URL, NEAR_NETWORK_ID, SWARM_ACCOUNTS
from backend.app.models import WalletInfo, AgentPayout, ContractSample

logger = logging.getLogger(__name__)

# Constants
YOCTO_NEAR = 10**24
DEFAULT_NEAR_CLI = r"C:\Users\USER\.cargo\bin\near.exe"
DEFAULT_CREDENTIALS_DIR = os.path.expanduser(r"~/.near-credentials/testnet")
BASE_PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
TEST_CONTRACTS_DIR = BASE_PROJECT_DIR / "test_contracts"


def get_near_cli_path() -> str:
    """Resolve the near CLI executable path."""
    custom_path = os.environ.get("NEAR_CLI_PATH", DEFAULT_NEAR_CLI)
    if os.path.exists(custom_path):
        return custom_path
    # Fallback to system PATH
    import shutil
    which_near = shutil.which("near")
    if which_near:
        return which_near
    return custom_path


def get_credentials_dir() -> Path:
    """Resolve the directory containing .near-credentials."""
    custom_dir = os.environ.get("NEAR_CREDENTIALS_DIR", DEFAULT_CREDENTIALS_DIR)
    p = Path(custom_dir)
    if p.exists():
        return p
    # Fallback to default user path
    alt = Path(os.path.expanduser(r"~\.near-credentials\testnet"))
    return alt


def query_rpc_raw(method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute raw JSON-RPC query against NEAR RPC."""
    payload = {
        "jsonrpc": "2.0",
        "id": "auditswarm_client",
        "method": method,
        "params": params,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        NEAR_RPC_URL,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=12.0) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_account_balance(account_id: str) -> Dict[str, Any]:
    """
    Query real balance & account state for any NEAR testnet account.
    Returns parsed NEAR balance, storage usage, and block metadata.
    """
    try:
        res = query_rpc_raw(
            "query",
            {
                "request_type": "view_account",
                "finality": "final",
                "account_id": account_id,
            },
        )
        if "result" in res and "amount" in res["result"]:
            r = res["result"]
            amount_yocto = int(r["amount"])
            balance_near = amount_yocto / YOCTO_NEAR
            return {
                "account_id": account_id,
                "amount_yocto": str(amount_yocto),
                "balance_near": balance_near,
                "balance_formatted": f"{balance_near:.4f}",
                "storage_usage_bytes": r.get("storage_usage", 0),
                "block_height": r.get("block_height", 0),
                "block_hash": r.get("block_hash", ""),
                "status": "ACTIVE",
            }
        elif "error" in res:
            logger.warning(f"NEAR RPC error querying {account_id}: {res['error']}")
            return {
                "account_id": account_id,
                "amount_yocto": "0",
                "balance_near": 0.0,
                "balance_formatted": "0.0000",
                "error": res["error"].get("message", "Unknown RPC error"),
                "status": "NOT_FOUND",
            }
    except Exception as e:
        logger.error(f"Failed to query account balance for {account_id}: {e}")
        return {
            "account_id": account_id,
            "amount_yocto": "0",
            "balance_near": 0.0,
            "balance_formatted": "0.0000",
            "error": str(e),
            "status": "ERROR",
        }
    return {
        "account_id": account_id,
        "amount_yocto": "0",
        "balance_near": 0.0,
        "balance_formatted": "0.0000",
        "status": "UNKNOWN",
    }


def get_agent_wallets_sync() -> List[WalletInfo]:
    """Synchronous fetch of all swarm agent wallet info and balances."""
    role_map = [
        ("main", "Treasury & Arbiter", SWARM_ACCOUNTS.get("main", "auditswarm-9003.testnet")),
        ("coordinator", "Swarm Coordinator", SWARM_ACCOUNTS.get("coordinator", "coordinator.auditswarm-9003.testnet")),
        ("hunter", "Static Hunter", SWARM_ACCOUNTS.get("hunter", "hunter.auditswarm-9003.testnet")),
        ("economic", "Economic Exploit Agent", SWARM_ACCOUNTS.get("economic", "economic.auditswarm-9003.testnet")),
        ("critic", "Red-Team Critic", SWARM_ACCOUNTS.get("critic", "critic.auditswarm-9003.testnet")),
    ]

    wallets: List[WalletInfo] = []
    for key, role_name, account_id in role_map:
        info = get_account_balance(account_id)
        bal_str = info.get("balance_formatted", "0.0000")
        wallets.append(
            WalletInfo(
                role=role_name,
                account_id=account_id,
                balance_near=bal_str,
                nearblocks_url=f"https://testnet.nearblocks.io/address/{account_id}",
                explorer_url=f"https://testnet.nearblocks.io/address/{account_id}",
            )
        )
    return wallets


async def get_agent_wallets() -> List[WalletInfo]:
    """Async wrapper to retrieve all swarm agent wallets."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_agent_wallets_sync)


def execute_payout_sync(
    receiver_id: str,
    amount_near: float,
    sender_id: Optional[str] = None,
) -> str:
    """
    Execute signed testnet token transfer using near CLI and local credentials.
    Returns on-chain Transaction ID (hash) upon success.
    """
    sender = sender_id or SWARM_ACCOUNTS.get("main", "auditswarm-9003.testnet")
    cli_path = get_near_cli_path()

    if amount_near <= 0.0:
        logger.info(f"Payout amount for {receiver_id} is 0. Skipping.")
        return "SKIPPED_ZERO_AMOUNT"

    # Format amount with up to 6 decimal places, e.g. 0.001 NEAR
    formatted_amount = f"{amount_near:.6f}".rstrip("0").rstrip(".")
    if not formatted_amount or formatted_amount == "0":
        formatted_amount = "0.0001"
    amount_arg = f"{formatted_amount} NEAR"

    cmd = [
        cli_path,
        "tokens",
        sender,
        "send-near",
        receiver_id,
        amount_arg,
        "network-config",
        NEAR_NETWORK_ID,
        "sign-with-keychain",
        "send",
    ]

    logger.info(f"Executing signed NEAR payout: {' '.join(cmd)}")

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
            check=False,
        )

        combined_output = proc.stdout + "\n" + proc.stderr

        # Check for Transaction ID pattern in output
        tx_match = re.search(r"Transaction ID:\s*([A-Za-z0-9]{30,60})", combined_output)
        if tx_match:
            tx_id = tx_match.group(1)
            logger.info(f"Payout confirmed! Tx ID: {tx_id}")
            return tx_id

        # Check for success message
        success_match = re.search(r"transferred [0-9.]+ NEAR to <([^>]+)> successfully", combined_output)
        if success_match and proc.returncode == 0:
            # Fallback tx identifier if tx id line wasn't parsed
            fallback_match = re.search(r"transactions/([A-Za-z0-9]{30,60})", combined_output)
            if fallback_match:
                return fallback_match.group(1)
            import hashlib, time
            return f"tx_conf_{hashlib.sha256(combined_output.encode()).hexdigest()[:32]}"

        if proc.returncode != 0:
            logger.error(f"near CLI payout failed with code {proc.returncode}:\n{combined_output}")
            raise RuntimeError(f"CLI error ({proc.returncode}): {proc.stderr.strip() or proc.stdout.strip()}")

        return "CONFIRMED"

    except subprocess.TimeoutExpired:
        logger.error("Timeout waiting for near CLI transaction submission.")
        raise TimeoutError("NEAR transaction submission timed out after 30 seconds")
    except Exception as e:
        logger.error(f"Failed to execute payout to {receiver_id}: {e}")
        raise


async def execute_payout(
    receiver_id: str,
    amount_near: float,
    sender_id: Optional[str] = None,
) -> str:
    """Async wrapper for signed payout execution."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        execute_payout_sync,
        receiver_id,
        amount_near,
        sender_id,
    )


async def execute_batch_payouts(payouts: List[AgentPayout]) -> List[AgentPayout]:
    """Execute payouts sequentially to prevent nonce collision."""
    for p in payouts:
        if p.reward_near > 0:
            try:
                tx_hash = await execute_payout(p.account_id, p.reward_near)
                p.tx_hash = tx_hash
                p.status = "CONFIRMED"
            except Exception as e:
                logger.error(f"Failed payout for {p.account_id}: {e}")
                p.status = "FAILED"
        else:
            p.status = "SKIPPED"
    return payouts


def load_test_contract(filename: str) -> str:
    """Load Rust source code for a test contract from test_contracts/."""
    path = TEST_CONTRACTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Contract file not found: {path}")
    return path.read_text(encoding="utf-8")


def get_sample_contracts() -> List[ContractSample]:
    """Return pre-packaged test contracts with vulnerability metadata."""
    samples = []

    vuln_path = TEST_CONTRACTS_DIR / "VulnerableVault.rs"
    if vuln_path.exists():
        samples.append(
            ContractSample(
                id="vulnerable_vault",
                name="VulnerableVault.rs",
                description="High-yield DeFi vault suffering from Cross-Contract Reentrancy/State Inconsistency, Share Rounding Inflation, and Unprotected Emergency Drain.",
                code=vuln_path.read_text(encoding="utf-8"),
                expected_vulnerabilities=[
                    "Cross-contract callback state inconsistency on withdraw",
                    "Economic share inflation attack on deposit_vault_shares",
                    "Broken access control in emergency_withdraw_all",
                    "Storage exhaustion DoS via unmetered dynamic collections",
                ],
            )
        )

    secure_path = TEST_CONTRACTS_DIR / "SecureEscrow.rs"
    if secure_path.exists():
        samples.append(
            ContractSample(
                id="secure_escrow",
                name="SecureEscrow.rs",
                description="Hardened multi-party escrow smart contract following Checks-Effects-Interactions, Safe Callback State Reversion, NEP-145 storage management, and NEP-297 event logging.",
                code=secure_path.read_text(encoding="utf-8"),
                expected_vulnerabilities=[],
            )
        )

    return samples
