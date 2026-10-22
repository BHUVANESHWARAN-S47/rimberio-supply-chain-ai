from backend.app.agents.base import BaseAgent
from backend.app.agents.registry import AgentRegistry, agent_registry
from backend.app.agents.buyer_agent import BuyerAgent, BuyerEvaluationInput
from backend.app.agents.supplier_agent import SupplierAgent
from backend.app.agents.price_analysis_agent import PriceAnalysisAgent
from backend.app.agents.logistics_agent import LogisticsAgent
from backend.app.agents.risk_agent import RiskAgent
from backend.app.agents.customer_impact_agent import CustomerImpactAgent
from backend.app.agents.adaptive_decision_agent import AdaptiveDecisionAgent
from backend.app.agents.supervisor_agent import SupervisorAgent
from backend.app.agents.explanation_agent import ExplanationAgent

# Register active instances in global singleton registry
agent_registry.register_class("BuyerAgent", BuyerAgent)
agent_registry.register_instance(BuyerAgent())

agent_registry.register_class("SupplierAgent", SupplierAgent)
agent_registry.register_instance(SupplierAgent())

agent_registry.register_class("PriceAnalysisAgent", PriceAnalysisAgent)
agent_registry.register_instance(PriceAnalysisAgent())

agent_registry.register_class("LogisticsAgent", LogisticsAgent)
agent_registry.register_instance(LogisticsAgent())

agent_registry.register_class("RiskAgent", RiskAgent)
agent_registry.register_instance(RiskAgent())

agent_registry.register_class("CustomerImpactAgent", CustomerImpactAgent)
agent_registry.register_instance(CustomerImpactAgent())

agent_registry.register_class("AdaptiveDecisionAgent", AdaptiveDecisionAgent)
agent_registry.register_instance(AdaptiveDecisionAgent())

agent_registry.register_class("SupervisorAgent", SupervisorAgent)
agent_registry.register_instance(SupervisorAgent())

agent_registry.register_class("ExplanationAgent", ExplanationAgent)
agent_registry.register_instance(ExplanationAgent())

__all__ = [
    "BaseAgent",
    "AgentRegistry",
    "agent_registry",
    "BuyerAgent",
    "BuyerEvaluationInput",
    "SupplierAgent",
    "PriceAnalysisAgent",
    "LogisticsAgent",
    "RiskAgent",
    "CustomerImpactAgent",
    "AdaptiveDecisionAgent",
    "SupervisorAgent",
    "ExplanationAgent",
]
