"""ADK entry point — re-exports root_agent from the main src package.

This wrapper exists so `adk run nexus_agent` works from the project root.
The actual orchestrator lives in src/agents/agent.py.
"""

import sys
from pathlib import Path

# Ensure the project root is on sys.path so `src.*` imports resolve
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.agents.agent import root_agent  # noqa: E402, F401
