from fastapi import APIRouter
from app.services.graph_service import GraphService

router = APIRouter()

@router.get("")
def get_routes():
    graph_svc = GraphService()
    try:
        routes = graph_svc.get_routes()
    finally:
        graph_svc.close()
    return routes
