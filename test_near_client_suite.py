import sys
import asyncio
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

from backend.app.near_client import (
    get_account_balance,
    get_agent_wallets_sync,
    get_agent_wallets,
    execute_payout_sync,
    load_test_contract,
    get_sample_contracts,
    SWARM_ACCOUNTS,
)

def test_balances():
    print("\n--- 1. Testing NEAR Testnet RPC Account Balances ---")
    for key, acct in SWARM_ACCOUNTS.items():
        res = get_account_balance(acct)
        print(f"[{key.upper()}] Account: {acct}")
        print(f"       Balance: {res['balance_formatted']} NEAR (Block: {res['block_height']}, Storage: {res['storage_usage_bytes']} bytes)")
        assert res["balance_near"] >= 0, f"Balance must be >= 0 for {acct}"
    print("PASS: Account balance queries successful via NEAR RPC.")

def test_wallets():
    print("\n--- 2. Testing Swarm Agent Wallets ---")
    wallets = get_agent_wallets_sync()
    assert len(wallets) == 5, f"Expected 5 wallets, got {len(wallets)}"
    for w in wallets:
        print(f"- {w.role}: {w.account_id} -> {w.balance_near} NEAR")
        print(f"  Explorer: {w.nearblocks_url}")
        assert "auditswarm-9003.testnet" in w.account_id
    print("PASS: Swarm agent wallets successfully constructed.")

def test_contracts():
    print("\n--- 3. Testing Sample Contracts ---")
    vuln = load_test_contract("VulnerableVault.rs")
    assert "VulnerableVault" in vuln
    assert "deposit_vault_shares" in vuln
    print(f"VulnerableVault.rs loaded successfully ({len(vuln)} bytes)")

    escrow = load_test_contract("SecureEscrow.rs")
    assert "SecureEscrow" in escrow
    assert "create_agreement" in escrow
    print(f"SecureEscrow.rs loaded successfully ({len(escrow)} bytes)")

    samples = get_sample_contracts()
    assert len(samples) == 2
    for s in samples:
        print(f"- Sample: {s.name} | Vulnerabilities: {len(s.expected_vulnerabilities)}")
    print("PASS: Sample contracts loaded and verified.")

def test_signed_payout():
    print("\n--- 4. Testing Signed NEAR Testnet Transfer ---")
    target = SWARM_ACCOUNTS["critic"]
    print(f"Sending 0.0005 NEAR micro-bounty to {target}...")
    tx_id = execute_payout_sync(
        receiver_id=target,
        amount_near=0.0005,
    )
    print(f"SUCCESS! Signed transaction submitted and confirmed!")
    print(f"Transaction ID: {tx_id}")
    print(f"View on Explorer: https://testnet.nearblocks.io/txns/{tx_id}")
    assert tx_id and len(tx_id) > 10, "Transaction ID should be non-empty string"
    print("PASS: Signed payout executed and confirmed.")

if __name__ == "__main__":
    print("=== STARTING AUDITSWARM NEAR CLIENT TEST SUITE ===")
    test_balances()
    test_wallets()
    test_contracts()
    test_signed_payout()
    print("\n=== ALL AUDITSWARM NEAR INTEGRATION TESTS PASSED! ===")
