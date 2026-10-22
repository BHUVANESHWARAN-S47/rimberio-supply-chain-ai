import os
import time
import json
import logging
from typing import Dict, Any, Optional
from backend.app.core.config import settings

os.makedirs(settings.LOG_DIR, exist_ok=True)

logger = logging.getLogger("rimberio")
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

class AgentTraceLogger:
    """Observability & audit tracer for autonomous multi-agent executions."""
    
    def __init__(self, trace_file: Optional[str] = None):
        self.trace_file = trace_file or os.path.join(settings.LOG_DIR, "agent_traces.jsonl")

    def record_execution(
        self,
        agent_name: str,
        execution_id: str,
        inputs: Dict[str, Any],
        output: Dict[str, Any],
        execution_time_ms: float,
        error: Optional[str] = None,
        model_used: Optional[str] = None,
        tokens_used: Optional[int] = None
    ) -> None:
        record = {
            "timestamp": time.time(),
            "agent_name": agent_name,
            "execution_id": execution_id,
            "inputs": inputs,
            "output": output,
            "execution_time_ms": execution_time_ms,
            "error": error,
            "model_used": model_used,
            "tokens_used": tokens_used
        }
        try:
            with open(self.trace_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, default=str) + "\n")
        except Exception as e:
            logger.error(f"Failed to write trace record: {e}")

tracer = AgentTraceLogger()
