import time
import uuid
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, TypeVar, Generic
from pydantic import BaseModel
from backend.app.schemas.common import AgentCapability
from backend.app.schemas.state import SupplyChainState
from backend.app.core.logging import logger, tracer

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")

class BaseAgent(ABC, Generic[TInput, TOutput]):
    """
    Abstract Base Class for all RIMBERIO autonomous supply chain agents.
    Enforces standardized execution, input/output validation, error handling,
    and execution tracing.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        capabilities: List[AgentCapability],
        db_session: Optional[Any] = None,
        llm_client: Optional[Any] = None,
        vector_store: Optional[Any] = None
    ):
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.db = db_session
        self.llm = llm_client
        self.vector_store = vector_store
        self.logger = logging.getLogger(f"rimberio.agent.{self.name}")

    @abstractmethod
    def validate_input(self, input_data: Any) -> TInput:
        """Validate and cast raw input into typed input schema."""
        pass

    @abstractmethod
    def run_deterministic_logic(self, validated_input: TInput, state: Optional[SupplyChainState] = None) -> TOutput:
        """Execute deterministic business calculations, constraints, and scoring."""
        pass

    def enrich_with_llm(self, output: TOutput, validated_input: TInput) -> TOutput:
        """Optional LLM enrichment for natural language reasoning or explanations."""
        return output

    def execute(self, input_data: Any, state: Optional[SupplyChainState] = None) -> TOutput:
        """
        Public entrypoint with standardized error handling, validation,
        and latency logging.
        """
        execution_id = str(uuid.uuid4())
        start_time = time.perf_counter()
        raw_inputs_dict = (
            input_data.model_dump() if isinstance(input_data, BaseModel) 
            else (input_data if isinstance(input_data, dict) else {"raw": str(input_data)})
        )
        
        self.logger.info(f"[{execution_id}] Starting execution of {self.name}...")
        error_msg = None
        
        try:
            # Step 1: Input Validation
            validated_input = self.validate_input(input_data)
            
            # Step 2: Deterministic Business Engine (No LLM hallucinations for math)
            result = self.run_deterministic_logic(validated_input, state)
            
            # Step 3: Optional LLM Enrichment (Explanations, reasoning)
            final_result = self.enrich_with_llm(result, validated_input)
            
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            if hasattr(final_result, "execution_time_ms"):
                final_result.execution_time_ms = round(elapsed_ms, 2)
                
            self.logger.info(f"[{execution_id}] Successfully executed {self.name} in {elapsed_ms:.2f}ms")
            
            # Record audit trace
            out_dict = (
                final_result.model_dump() if isinstance(final_result, BaseModel) 
                else (final_result if isinstance(final_result, dict) else {"result": str(final_result)})
            )
            tracer.record_execution(
                agent_name=self.name,
                execution_id=execution_id,
                inputs=raw_inputs_dict,
                output=out_dict,
                execution_time_ms=elapsed_ms
            )
            return final_result

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            error_msg = str(e)
            self.logger.error(f"[{execution_id}] Failed execution in {self.name}: {error_msg}", exc_info=True)
            tracer.record_execution(
                agent_name=self.name,
                execution_id=execution_id,
                inputs=raw_inputs_dict,
                output={},
                execution_time_ms=elapsed_ms,
                error=error_msg
            )
            raise e
