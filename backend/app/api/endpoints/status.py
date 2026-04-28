from fastapi import APIRouter
from app.services.graph_service import GraphService

router = APIRouter()

@router.get("")
def get_status():
    graph_svc = GraphService()
    try:
        nodes = graph_svc.get_all_nodes()
        db_status = "connected"
    except Exception as e:
        nodes = []
        db_status = f"error: {str(e)}"
    finally:
        graph_svc.close()
        
    return {
        "system": "online",
        "neo4j": db_status,
        "nodes": nodes
    }
