import networkx as nx
from typing import List
from app.core.config import settings

class DecisionService:
    def decide(
        self,
        risk: float,
        G: nx.DiGraph,
        source: str,
        target: str,
        routing_service
    ) -> dict:
        threshold = settings.reroute_risk_threshold

        if risk > threshold:
            rerouted_path = routing_service.shortest_path(G, source, target)
            return {
                "action": "reroute",
                "risk_score": risk,
                "recommended_path": rerouted_path,
                "reason": f"Predicted risk {risk:.2f} exceeds threshold {threshold}"
            }

        return {
            "action": "continue",
            "risk_score": risk,
            "recommended_path": None,
            "reason": "Risk within acceptable limits"
        }
