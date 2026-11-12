import os
from pathlib import Path
from dotenv import dotenv_values, load_dotenv

# Try finding .env.local and .env in current and parent directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_local_path = BASE_DIR / ".env.local"
env_path = BASE_DIR / ".env"

config_map = {}
if env_local_path.exists():
    config_map.update(dotenv_values(env_local_path))
if env_path.exists():
    config_map.update(dotenv_values(env_path))

# Also read process environment variables
for k, v in os.environ.items():
    if k not in config_map or not config_map[k]:
        config_map[k] = v

# LLM Configuration
MUSE_MODEL = config_map.get("MUSE_MODEL", "muse-spark-1.3-contributor")
_raw_base_url = config_map.get("MUSE_BASE_URL", "https://api.meta.ai/v1").rstrip("/")
if _raw_base_url.endswith("/chat/completions"):
    _raw_base_url = _raw_base_url[:-17]
MUSE_BASE_URL = _raw_base_url
MUSE_API_KEY = config_map.get("MUSE_API_KEY", "")

MAX_TOKENS = int(config_map.get("MAX_TOKENS", 4096))
TEMPERATURE = float(config_map.get("TEMPERATURE", 0.2))

# NEAR Configuration
NEAR_RPC_URL = config_map.get("NEAR_RPC_URL", "https://rpc.testnet.near.org")
NEAR_NETWORK_ID = config_map.get("NEAR_NETWORK_ID", "testnet")

# Swarm Testnet Accounts
SWARM_ACCOUNTS = {
    "main": config_map.get("SWARM_MAIN_ACCOUNT", "auditswarm-9003.testnet"),
    "coordinator": config_map.get("SWARM_COORDINATOR_ACCOUNT", "coordinator.auditswarm-9003.testnet"),
    "hunter": config_map.get("SWARM_HUNTER_ACCOUNT", "hunter.auditswarm-9003.testnet"),
    "economic": config_map.get("SWARM_ECONOMIC_ACCOUNT", "economic.auditswarm-9003.testnet"),
    "critic": config_map.get("SWARM_CRITIC_ACCOUNT", "critic.auditswarm-9003.testnet"),
}

SERVER_HOST = config_map.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(config_map.get("SERVER_PORT", 8000))
