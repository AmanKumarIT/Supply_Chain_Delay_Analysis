import networkx as nx
from typing import List, Dict, Any

class RoutingService:
    def build_graph(self, routes: List[Dict[str, Any]]) -> nx.DiGraph:
        G = nx.DiGraph()
        for r in routes:
            G.add_edge(
                r["source"],
                r["target"],
                weight=r["time"],
                cost=r["cost"],
                distance=r["distance"]
            )
        return G

    def shortest_path(self, G: nx.DiGraph, source: str, target: str) -> List[str]:
        try:
            return nx.shortest_path(G, source=source, target=target, weight="weight")
        except nx.NetworkXNoPath:
            return []

    def all_simple_paths(self, G: nx.DiGraph, source: str, target: str) -> List[List[str]]:
        try:
            return list(nx.all_simple_paths(G, source=source, target=target))
        except nx.NetworkXNoPath:
            return []
