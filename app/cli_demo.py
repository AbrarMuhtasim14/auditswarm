import sys
from pathlib import Path

# Add backend to sys.path
backend_path = Path(__file__).resolve().parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from backend.app.cli_demo import main

if __name__ == "__main__":
    main()
