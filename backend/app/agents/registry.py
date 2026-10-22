import logging
from typing import Dict, List, Optional, Type, Any
from backend.app.agents.base import BaseAgent
from backend.app.schemas.common import AgentCapability

logger = logging.getLogger("rimberio.agent_registry")

class AgentRegistry:
    """Central registry and factory for all autonomous RIMBERIO agents."""
    
    _classes: Dict[str, Type[BaseAgent]] = {}
    _metadata: Dict[str, Dict[str, Any]] = {}
    _registry: Dict[str, BaseAgent] = {}

    def __init__(self):
        pass

    @classmethod
    def register(
        cls,
        name: str,
        agent_class: Type[BaseAgent],
        capabilities: Optional[List[AgentCapability]] = None,
        version: str = "1.0.0"
    ) -> None:
        """Classmethod to register an agent class and its metadata."""
        cls._classes[name] = agent_class
        cls._metadata[name] = {
            "name": name,
            "class": agent_class,
            "capabilities": capabilities or [],
            "version": version
        }
        logger.info(f"Registered agent: {name} (v{version})")

    @classmethod
    def get_agent_class(cls, name: str) -> Optional[Type[BaseAgent]]:
        """Retrieve registered agent class."""
        return cls._classes.get(name)

    @classmethod
    def get_agent_metadata(cls, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve metadata for a registered agent."""
        return cls._metadata.get(name)

    def register_class(self, agent_name: str, agent_cls: Type[BaseAgent]) -> None:
        """Register an agent class type on instance."""
        self._classes[agent_name] = agent_cls
        logger.info(f"Registered agent class: {agent_name}")

    def register_instance(self, agent: BaseAgent) -> None:
        """Register an active singleton agent instance."""
        self._registry[agent.name] = agent
        logger.info(f"Registered active agent instance: {agent.name}")

    def get(self, agent_name: str) -> Optional[BaseAgent]:
        """Retrieve an agent instance by name."""
        return self._registry.get(agent_name)

    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents and their capabilities."""
        return [
            {
                "name": agent.name,
                "description": agent.description,
                "capabilities": [c.value for c in agent.capabilities]
            }
            for agent in self._registry.values()
        ]

    def find_by_capability(self, capability: AgentCapability) -> List[BaseAgent]:
        """Find agents providing a specific capability."""
        return [
            agent for agent in self._registry.values()
            if capability in agent.capabilities
        ]

agent_registry = AgentRegistry()
