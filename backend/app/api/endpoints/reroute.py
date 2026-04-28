from fastapi import APIRouter
from pydantic import BaseModel
from app.services.graph_service import GraphService
from app.services.routing_service import RoutingService

router = APIRouter()

class RerouteRequest(BaseModel):
    source: str
    target: str

@router.post("")
def reroute(req: RerouteRequest):
    graph_svc = GraphService()
    routing_svc = RoutingService()
    
    routes = graph_svc.get_routes()
    G = routing_svc.build_graph(routes)
    
    recommended_path = routing_svc.shortest_path(G, req.source, req.target)
    
    return {
        "action": "reroute",
        "recommended_path": recommended_path
    }
