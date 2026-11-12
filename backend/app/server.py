import json
import logging
from typing import Dict, Optional, List
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from backend.app.config import (
    MUSE_MODEL,
    MUSE_BASE_URL,
    NEAR_RPC_URL,
    SWARM_ACCOUNTS,
    SERVER_HOST,
    SERVER_PORT
)
from backend.app.models import (
    AuditRequest,
    AuditResult,
    WalletInfo,
    ContractSample
)
from backend.app.graph import stream_audit_events, run_audit_full
from backend.app.near_adapter import get_all_agent_wallets
from backend.app.contracts import get_available_contracts, get_contract_by_id, get_contract_code

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("audit_server")

app = FastAPI(
    title="NEAR Multi-Agent Adversarial Audit Swarm API",
    description="LangGraph multi-agent adversarial debate graph for NEAR smart contract security audits",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for completed audits
AUDIT_STORE: Dict[str, AuditResult] = {}

@app.get("/")
async def root():
    return {
        "service": "NEAR Multi-Agent Adversarial Audit Swarm",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_url": "/api/health",
        "wallets_url": "/api/wallets",
        "contracts_url": "/api/contracts"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "llm_model": MUSE_MODEL,
        "llm_base_url": MUSE_BASE_URL,
        "near_rpc": NEAR_RPC_URL,
        "accounts": SWARM_ACCOUNTS
    }

@app.get("/api/wallets", response_model=List[WalletInfo])
@app.get("/api/accounts/balances", response_model=List[WalletInfo])
async def get_wallets():
    """Retrieve live balances and explorer links for all 5 swarm agent wallets."""
    return await get_all_agent_wallets()

@app.get("/api/contracts", response_model=List[ContractSample])
@app.get("/api/contracts/samples", response_model=List[ContractSample])
async def list_contracts():
    """List preloaded audit test contracts (VulnerableVault.rs, SecureEscrow.rs)."""
    return get_available_contracts()

@app.get("/api/contracts/{contract_id}", response_model=ContractSample)
async def get_contract(contract_id: str):
    """Retrieve a single test contract by ID or name."""
    contract = get_contract_by_id(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail=f"Contract '{contract_id}' not found.")
    return contract

# --- SSE Streaming Endpoints ---

async def sse_event_wrapper(generator):
    """Wraps dictionary events into sse-starlette format."""
    try:
        async for event in generator:
            # Save final result into store if audit completes
            if event.get("event") == "audit_complete":
                try:
                    res_obj = AuditResult(**event["data"])
                    AUDIT_STORE[res_obj.audit_id] = res_obj
                except Exception as ex:
                    logger.warning(f"Failed to cache audit in store: {ex}")

            yield {
                "event": event["event"],
                "data": json.dumps(event["data"])
            }
    except Exception as e:
        logger.error(f"Error in SSE stream: {e}", exc_info=True)
        yield {
            "event": "error",
            "data": json.dumps({"error": str(e)})
        }

@app.post("/api/audit/stream")
async def stream_audit_post(req: AuditRequest):
    """SSE streaming endpoint accepting JSON payload."""
    generator = stream_audit_events(
        contract_name=req.contract_name,
        contract_code=req.contract_code,
        bounty_pool_near=req.bounty_pool_near,
        execute_real_payout=req.execute_real_payout
    )
    return EventSourceResponse(sse_event_wrapper(generator))

@app.get("/api/audit/stream")
async def stream_audit_get(
    contract_name: Optional[str] = Query("VulnerableVault.rs"),
    contract_code: Optional[str] = Query(None),
    bounty_pool_near: float = Query(1.0),
    execute_real_payout: bool = Query(True)
):
    """SSE streaming endpoint accepting GET query params (for standard EventSource)."""
    code = contract_code
    if not code:
        code = get_contract_code(contract_name)

    generator = stream_audit_events(
        contract_name=contract_name,
        contract_code=code,
        bounty_pool_near=bounty_pool_near,
        execute_real_payout=execute_real_payout
    )
    return EventSourceResponse(sse_event_wrapper(generator))

@app.post("/api/audit", response_model=AuditResult)
async def create_audit(req: AuditRequest):
    """Run an audit synchronously and return the complete result."""
    result = await run_audit_full(
        contract_name=req.contract_name,
        contract_code=req.contract_code,
        bounty_pool_near=req.bounty_pool_near,
        execute_real_payout=req.execute_real_payout
    )
    AUDIT_STORE[result.audit_id] = result
    return result

@app.get("/api/audit/{audit_id}", response_model=AuditResult)
async def get_audit_result(audit_id: str):
    """Retrieve the result of a completed or active audit."""
    if audit_id not in AUDIT_STORE:
        raise HTTPException(status_code=404, detail=f"Audit '{audit_id}' not found.")
    return AUDIT_STORE[audit_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.server:app", host=SERVER_HOST, port=SERVER_PORT, reload=True)
