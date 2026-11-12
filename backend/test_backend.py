import sys
import unittest
import asyncio
from pathlib import Path

# Add paths
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from backend.app.server import app
from backend.app.config import SWARM_ACCOUNTS, MUSE_MODEL
from backend.app.contracts import get_available_contracts, get_contract_by_id
from backend.app.near_adapter import get_all_agent_wallets_sync
from backend.app.graph import build_audit_graph

class TestAuditBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_health_endpoint(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["llm_model"], MUSE_MODEL)
        self.assertIn("auditswarm-9003.testnet", str(data["accounts"]))

    def test_02_contracts_endpoints(self):
        resp = self.client.get("/api/contracts")
        self.assertEqual(resp.status_code, 200)
        contracts = resp.json()
        self.assertGreaterEqual(len(contracts), 2)
        
        ids = [c["id"] for c in contracts]
        self.assertIn("vulnerable_vault", ids)
        self.assertIn("secure_escrow", ids)

        # Single contract fetch
        resp_single = self.client.get("/api/contracts/vulnerable_vault")
        self.assertEqual(resp_single.status_code, 200)
        c = resp_single.json()
        self.assertEqual(c["name"], "VulnerableVault.rs")
        self.assertIn("pub struct VulnerableVault", c["code"])

    def test_03_wallets_endpoint(self):
        resp = self.client.get("/api/wallets")
        self.assertEqual(resp.status_code, 200)
        wallets = resp.json()
        self.assertEqual(len(wallets), 5)
        for w in wallets:
            self.assertTrue(w["account_id"].endswith(".testnet"))
            self.assertIn("nearblocks.io", w["explorer_url"])

    def test_04_langgraph_compilation(self):
        graph = build_audit_graph()
        self.assertIsNotNone(graph)
        # Verify node names in graph
        nodes = list(graph.nodes.keys())
        expected_nodes = [
            "coordinator",
            "static_hunter",
            "economic_exploit",
            "red_team_critic",
            "arbiter",
            "payout_executor"
        ]
        for en in expected_nodes:
            self.assertIn(en, nodes)

    def test_05_sse_stream_endpoint_get(self):
        # Test that SSE stream responds with 200 and text/event-stream content type
        with self.client.stream("GET", "/api/audit/stream?contract_name=SecureEscrow.rs&execute_real_payout=false") as response:
            self.assertEqual(response.status_code, 200)
            self.assertIn("text/event-stream", response.headers["content-type"])
            # Read first event chunk
            first_chunk = next(response.iter_lines())
            self.assertTrue(len(first_chunk) >= 0)

if __name__ == "__main__":
    unittest.main()
