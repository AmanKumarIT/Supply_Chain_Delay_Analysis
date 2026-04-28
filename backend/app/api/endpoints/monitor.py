"""
Monitor endpoint — called by the frontend on a polling interval after
the initial sweep. Re-checks live weather along the active route and
returns alerts ONLY if the predicted delay factor crosses the threshold.
"""
from fastapi import APIRouter, Query
from app.services.graph_service import GraphService
from app.services.routing_service import RoutingService
from app.services.geo_routing_service import GeoRoutingService
from app.services.weather_service import WeatherService
from app.ml.predictor import predict_delay
from app.core.config import settings

router = APIRouter()


@router.get("")
async def monitor_route(
    source: str = Query(..., description="Source city name"),
    target: str = Query(..., description="Target city name"),
):
    # 1. Recompute logical + geo route
    graph_svc = GraphService()
    routing_svc = RoutingService()
    routes = graph_svc.get_routes()
    G = routing_svc.build_graph(routes)
    logical_path = routing_svc.shortest_path(G, source, target)
    if not logical_path:
        logical_path = [source, target]

    geo_svc = GeoRoutingService()
    geometry = geo_svc.get_multi_hop_geometry(logical_path)

    # 2. Fetch fresh weather
    weather_svc = WeatherService()
    weather_data = await weather_svc.get_route_weather(geometry["coords"])
    weather_severity = weather_data["severity"]

    # 3. Run ML prediction
    distance = geometry["distance_km"]
    prediction = predict_delay(distance, weather_severity, 0.3, 0.4)
    risk = prediction["risk_score"]

    threshold = settings.reroute_risk_threshold

    # 4. Only generate alerts if risk exceeds threshold
    if risk > threshold:
        # Build a detailed alert
        alert_details = {
            "status": "ALERT",
            "risk_score": risk,
            "threshold": threshold,
            "predicted_delay_hours": prediction["predicted_delay_hours"],
            "weather_severity": weather_severity,
            "weather_alerts": weather_data["alerts"],
            "weather_details": weather_data["details"],
            "reason": (
                f"Risk {risk:.2f} exceeds threshold {threshold}. "
                f"Weather severity: {weather_severity:.2f}. "
                f"Predicted delay: {prediction['predicted_delay_hours']}h."
            ),
            "recommendation": "REROUTE",
        }
        return alert_details

    # Below threshold — no alert, just nominal status
    return {
        "status": "NOMINAL",
        "risk_score": risk,
        "threshold": threshold,
        "predicted_delay_hours": prediction["predicted_delay_hours"],
        "weather_severity": weather_severity,
        "weather_details": weather_data["details"],
        "reason": "Route conditions within acceptable limits",
    }
