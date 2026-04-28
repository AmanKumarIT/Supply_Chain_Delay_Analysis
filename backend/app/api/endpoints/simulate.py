from fastapi import APIRouter
from pydantic import BaseModel
from app.services.graph_service import GraphService
from app.services.routing_service import RoutingService
from app.services.decision_service import DecisionService
from app.services.geo_routing_service import GeoRoutingService
from app.services.weather_service import WeatherService
from app.ml.predictor import predict_delay

router = APIRouter()


class SimulateRequest(BaseModel):
    source: str
    target: str
    # weather and traffic are now fetched automatically from live APIs


@router.post("")
async def simulate(req: SimulateRequest):
    # 1. Logical routing via NetworkX (which cities to traverse)
    graph_svc = GraphService()
    routing_svc = RoutingService()
    decision_svc = DecisionService()

    routes = graph_svc.get_routes()
    G = routing_svc.build_graph(routes)
    logical_path = routing_svc.shortest_path(G, req.source, req.target)

    if not logical_path:
        logical_path = [req.source, req.target]

    # 2. Geo routing via OSMnx (resolve to real road coordinates)
    geo_svc = GeoRoutingService()
    geometry = geo_svc.get_multi_hop_geometry(logical_path)

    # 3. Live weather along the route
    weather_svc = WeatherService()
    weather_data = await weather_svc.get_route_weather(geometry["coords"])
    weather_severity = weather_data["severity"]

    # 4. ML prediction using real weather + computed distance
    distance = geometry["distance_km"]
    traffic = 0.3  # baseline traffic estimate (can be enhanced later)
    congestion = 0.4

    prediction = predict_delay(distance, weather_severity, traffic, congestion)
    risk = prediction["risk_score"]

    # 5. Decision engine
    decision = decision_svc.decide(risk, G, req.source, req.target, routing_svc)

    # 6. If reroute is triggered, compute the alternate road geometry too
    reroute_geometry = None
    if decision["action"] == "reroute" and decision.get("recommended_path"):
        reroute_geometry = geo_svc.get_multi_hop_geometry(
            decision["recommended_path"]
        )

    return {
        "input": {"source": req.source, "target": req.target},
        "prediction": prediction,
        "decision": decision,
        "route_geometry": geometry,
        "reroute_geometry": reroute_geometry,
        "weather_data": weather_data,
    }
